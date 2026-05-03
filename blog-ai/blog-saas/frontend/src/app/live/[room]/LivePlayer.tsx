"use client";
import { memo, useRef, useEffect } from "react";
import { Room, RoomEvent, Track } from "livekit-client";

interface Props {
  token: string;
  serverUrl: string;
  isHost: boolean;
  hostName?: string;
  /** Room name + auth bearer token — only set when this player is the original host;
   *  used to upload periodic thumbnail frames so the /live feed shows real video. */
  roomName?: string;
  authToken?: string | null;
}

const LivePlayer = memo(function LivePlayer({ token, serverUrl, isHost, hostName, roomName, authToken }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const roomRef = useRef<Room | null>(null);
  const localVideoRef = useRef<HTMLVideoElement | null>(null);

  function attachVideoTrack(track: any, participantName?: string, isLocal = false) {
    if (!containerRef.current) return;
    // Check if track already attached
    const existingId = `track-${track.sid || Math.random()}`;
    if (containerRef.current.querySelector(`[data-track-id="${existingId}"]`)) return;

    const wrapper = document.createElement("div");
    wrapper.setAttribute("data-track-id", existingId);
    wrapper.style.cssText = "position:relative;flex:1;min-width:0;height:100%;";

    const el = track.attach() as HTMLVideoElement;
    el.style.cssText = "width:100%;height:100%;object-fit:contain;background:#000;";
    el.autoplay = true;
    el.playsInline = true;
    el.muted = isHost;

    if (isLocal) localVideoRef.current = el;

    const label = document.createElement("div");
    label.style.cssText = "position:absolute;bottom:8px;left:8px;font-size:0.6rem;color:#fff;font-family:monospace;background:rgba(0,0,0,0.6);padding:2px 6px;border-radius:2px;";
    label.textContent = participantName || "";

    wrapper.appendChild(el);
    if (participantName) wrapper.appendChild(label);

    // Remove placeholder
    const placeholder = containerRef.current.querySelector(".lk-placeholder");
    if (placeholder) placeholder.remove();

    containerRef.current.appendChild(wrapper);

    // Update layout — flex row
    containerRef.current.style.cssText = "width:100%;height:100%;background:#000;display:flex;flex-direction:row;";
  }

  useEffect(() => {
    if (roomRef.current) return;
    const room = new Room({ adaptiveStream: true, dynacast: true });
    roomRef.current = room;
    let thumbnailInterval: ReturnType<typeof setInterval> | null = null;
    let firstThumbTimeout: ReturnType<typeof setTimeout> | null = null;

    room.on(RoomEvent.TrackSubscribed, (track: any, pub: any, participant: any) => {
      if (track.kind === Track.Kind.Video) attachVideoTrack(track, participant?.name || participant?.identity);
      else if (track.kind === Track.Kind.Audio && !isHost) {
        const el = track.attach();
        document.body.appendChild(el);
      }
    });

    // When a new participant joins with tracks already published
    room.on(RoomEvent.ParticipantConnected, (participant: any) => {
      participant.trackPublications.forEach((pub: any) => {
        if (pub.track && pub.isSubscribed) {
          if (pub.kind === Track.Kind.Video) attachVideoTrack(pub.track);
        }
      });
    });

    // When a track is published (before subscribed)
    room.on(RoomEvent.TrackPublished, (pub: any, participant: any) => {
      if (!isHost) {
        // Auto-subscribe
        setTimeout(() => {
          if (pub.track) {
            if (pub.kind === Track.Kind.Video) attachVideoTrack(pub.track);
            else if (pub.kind === Track.Kind.Audio) {
              const el = pub.track.attach();
              document.body.appendChild(el);
            }
          }
        }, 500);
      }
    });

    room.on(RoomEvent.TrackUnsubscribed, (track: any) => { track.detach(); });

    room.on(RoomEvent.DataReceived, (payload: Uint8Array) => {
      try {
        const msg = JSON.parse(new TextDecoder().decode(payload));
        const overlay = document.getElementById("host-status-overlay");
        if (overlay) overlay.style.display = msg.type === "host_paused" ? "flex" : "none";
      } catch {}
    });

    room.connect(serverUrl, token).then(async () => {
      if (isHost) {
        await room.localParticipant.enableCameraAndMicrophone();
        room.localParticipant.trackPublications.forEach((pub) => {
          if (pub.track && pub.kind === Track.Kind.Video) {
            attachVideoTrack(pub.track, room.localParticipant.name, true);
          }
        });
        document.addEventListener("visibilitychange", () => {
          try {
            const msg = document.hidden ? "host_paused" : "host_resumed";
            room.localParticipant.publishData(new TextEncoder().encode(JSON.stringify({ type: msg })), { reliable: true });
          } catch {}
        });

        // Periodic thumbnail capture — host only. Captures the local video into
        // a 320×180 JPEG and POSTs to the backend so /live shows real frames.
        if (roomName && authToken) {
          const captureAndUpload = () => {
            const v = localVideoRef.current;
            if (!v) {
              console.warn("[thumbnail] no local video element yet — skip");
              return;
            }
            if (v.videoWidth === 0 || v.readyState < 2) {
              console.warn(`[thumbnail] video not ready — skip (w=${v.videoWidth} state=${v.readyState})`);
              return;
            }
            const canvas = document.createElement("canvas");
            canvas.width = 320;
            canvas.height = 180;
            const ctx = canvas.getContext("2d");
            if (!ctx) {
              console.warn("[thumbnail] canvas ctx unavailable — skip");
              return;
            }
            try {
              ctx.drawImage(v, 0, 0, 320, 180);
            } catch (err) {
              console.warn("[thumbnail] drawImage failed (CORS?):", err);
              return;
            }
            canvas.toBlob(async (blob) => {
              if (!blob) {
                console.warn("[thumbnail] toBlob produced null");
                return;
              }
              try {
                const r = await fetch(`/api/proxy/live/${roomName}/thumbnail`, {
                  method: "POST",
                  headers: {
                    "Content-Type": "image/jpeg",
                    Authorization: `Bearer ${authToken}`,
                  },
                  body: blob,
                });
                if (!r.ok) {
                  const body = await r.text().catch(() => "<empty>");
                  console.warn(`[thumbnail] upload returned ${r.status}: ${body.slice(0, 200)}`);
                } else {
                  console.log(`[thumbnail] uploaded (${Math.round(blob.size / 1024)}KB)`);
                }
              } catch (err) {
                console.warn("[thumbnail] upload error:", err);
              }
            }, "image/jpeg", 0.7);
          };
          // First capture after 5s (give the camera time to produce frames),
          // then every 30s for the rest of the stream.
          firstThumbTimeout = setTimeout(captureAndUpload, 5000);
          thumbnailInterval = setInterval(captureAndUpload, 30000);
        }
      } else {
        // Attach existing tracks immediately
        room.remoteParticipants.forEach((p) => {
          p.trackPublications.forEach((pub) => {
            if (pub.isSubscribed && pub.track) {
              if (pub.kind === Track.Kind.Video) attachVideoTrack(pub.track);
              else if (pub.kind === Track.Kind.Audio) { const el = pub.track.attach(); document.body.appendChild(el); }
            }
          });
        });
      }
    }).catch(console.error);

    return () => {
      if (firstThumbTimeout) clearTimeout(firstThumbTimeout);
      if (thumbnailInterval) clearInterval(thumbnailInterval);
      room.disconnect();
      roomRef.current = null;
    };
  }, []);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <div ref={containerRef} style={{ width: "100%", height: "100%", background: "#000", display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
        <p className="lk-placeholder" style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.1em", position: "relative", zIndex: 1 }}>
          {isHost ? "Starting camera..." : "Waiting for host..."}
        </p>
      </div>
      <div id="host-status-overlay" style={{ display: "none", position: "absolute", inset: 0, background: "rgba(0,0,0,0.75)", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: "0.5rem" }}>
        <p style={{ color: "#f0e8d8", fontFamily: "Georgia, serif", fontSize: "1rem", margin: 0 }}>📵 {hostName || "Host"} paused their video</p>
        <p style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem", margin: 0 }}>Stream will resume shortly...</p>
      </div>
    </div>
  );
}, () => true);

export default LivePlayer;
