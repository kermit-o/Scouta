"use client";
import { useEffect, useRef } from "react";
import { useTracks } from "@livekit/components-react";
import { Track } from "livekit-client";

function VideoTrack({ trackRef }: { trackRef: any }) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const track = trackRef?.publication?.track;
    const el = videoRef.current;
    if (!track || !el) return;
    track.attach(el);
    return () => { track.detach(el); };
  }, [trackRef]);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      style={{ width: "100%", height: "100%", objectFit: "contain" }}
    />
  );
}

export default function TrackPlayer({ isHost }: { isHost: boolean }) {
  const tracks = useTracks(
    [
      { source: Track.Source.Camera, withPlaceholder: false },
      { source: Track.Source.ScreenShare, withPlaceholder: false },
    ],
    { onlySubscribed: !isHost }
  );

  if (tracks.length === 0) {
    return (
      <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", background: "#000" }}>
        <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.1em" }}>
          {isHost ? "Camera starting..." : "Waiting for host..."}
        </p>
      </div>
    );
  }

  return (
    <div style={{ width: "100%", height: "100%", background: "#000", display: "flex" }}>
      {tracks.map((track) => (
        <div
          key={`${track.participant.identity}-${track.source}`}
          style={{ flex: 1, position: "relative", minWidth: 0 }}
        >
          <VideoTrack trackRef={track} />
          <div style={{
            position: "absolute", bottom: 8, left: 8,
            fontSize: "0.6rem", color: "#fff", fontFamily: "monospace",
            background: "rgba(0,0,0,0.6)", padding: "2px 6px", borderRadius: 2,
          }}>
            {track.participant.name || track.participant.identity}
            {track.participant.isLocal && " (you)"}
          </div>
        </div>
      ))}
    </div>
  );
}
