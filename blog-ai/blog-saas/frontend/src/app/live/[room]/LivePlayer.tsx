"use client";
import { memo, useRef, useEffect } from "react";
import { Room, RoomEvent, Track, RemoteTrack, RemoteTrackPublication, RemoteParticipant } from "livekit-client";

interface Props {
  token: string;
  serverUrl: string;
  isHost: boolean;
}

const LivePlayer = memo(function LivePlayer({ token, serverUrl, isHost }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const roomRef = useRef<Room | null>(null);

  useEffect(() => {
    if (roomRef.current) return; // already connected

    const room = new Room({
      adaptiveStream: true,
      dynacast: true,
    });
    roomRef.current = room;

    function handleTrackSubscribed(track: RemoteTrack, pub: RemoteTrackPublication, participant: RemoteParticipant) {
      if (!containerRef.current) return;
      if (track.kind === Track.Kind.Video) {
        const el = track.attach();
        el.style.width = "100%";
        el.style.height = "100%";
        el.style.objectFit = "contain";
        el.autoplay = true;
        el.playsInline = true;
        containerRef.current.innerHTML = "";
        containerRef.current.appendChild(el);
      } else if (track.kind === Track.Kind.Audio) {
        const el = track.attach();
        document.body.appendChild(el);
      }
    }

    function handleTrackUnsubscribed(track: RemoteTrack) {
      track.detach();
    }

    room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed);
    room.on(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed);

    room.connect(serverUrl, token).then(async () => {
      if (isHost) {
        await room.localParticipant.enableCameraAndMicrophone();
        const videoTrack = room.localParticipant.getTrackPublication(Track.Source.Camera)?.track;
        if (videoTrack && containerRef.current) {
          const el = videoTrack.attach();
          el.style.width = "100%";
          el.style.height = "100%";
          el.style.objectFit = "contain";
          el.autoplay = true;
          el.playsInline = true;
          el.muted = true;
          containerRef.current.innerHTML = "";
          containerRef.current.appendChild(el);
        }
      }
    }).catch(console.error);

    return () => {
      room.disconnect();
      roomRef.current = null;
    };
  }, []); // empty deps — only mount once

  return (
    <div ref={containerRef} style={{ width: "100%", height: "100%", background: "#000", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.1em" }}>
        {isHost ? "Starting camera..." : "Waiting for host..."}
      </p>
    </div>
  );
}, () => true); // never re-render

export default LivePlayer;
