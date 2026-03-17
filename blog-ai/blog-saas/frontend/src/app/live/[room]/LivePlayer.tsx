"use client";
import { memo, useRef, useEffect } from "react";
import { Room, RoomEvent, Track } from "livekit-client";

interface Props {
  token: string;
  serverUrl: string;
  isHost: boolean;
  hostName?: string;
}

const LivePlayer = memo(function LivePlayer({ token, serverUrl, isHost, hostName }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const roomRef = useRef<Room | null>(null);

  function attachVideoTrack(track: any) {
    if (!containerRef.current) return;
    const el = track.attach() as HTMLVideoElement;
    el.style.cssText = "width:100%;height:100%;object-fit:contain;background:#000;position:absolute;inset:0;";
    el.autoplay = true;
    el.playsInline = true;
    el.muted = isHost;
    const placeholder = containerRef.current.querySelector(".lk-placeholder");
    if (placeholder) placeholder.remove();
    containerRef.current.appendChild(el);
  }

  useEffect(() => {
    if (roomRef.current) return;
    const room = new Room({ adaptiveStream: true, dynacast: true });
    roomRef.current = room;

    room.on(RoomEvent.TrackSubscribed, (track: any) => {
      if (track.kind === Track.Kind.Video) attachVideoTrack(track);
      else if (track.kind === Track.Kind.Audio && !isHost) {
        const el = track.attach();
        document.body.appendChild(el);
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
          if (pub.track && pub.kind === Track.Kind.Video) attachVideoTrack(pub.track);
        });
        document.addEventListener("visibilitychange", () => {
          try {
            const msg = document.hidden ? "host_paused" : "host_resumed";
            room.localParticipant.publishData(new TextEncoder().encode(JSON.stringify({ type: msg })), { reliable: true });
          } catch {}
        });
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

    return () => { room.disconnect(); roomRef.current = null; };
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
