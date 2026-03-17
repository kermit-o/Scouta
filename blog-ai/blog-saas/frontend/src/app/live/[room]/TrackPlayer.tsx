"use client";
import { useEffect, useRef } from "react";
import { useTracks, useRoomContext } from "@livekit/components-react";
import { Track, RoomEvent } from "livekit-client";

function VideoTrack({ track }: { track: any }) {
  const ref = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    if (ref.current && track.publication?.track) {
      track.publication.track.attach(ref.current);
      return () => { track.publication?.track?.detach(ref.current!); };
    }
  }, [track]);
  return (
    <video
      ref={ref}
      autoPlay
      playsInline
      muted={track.source === Track.Source.Camera}
      style={{ width: "100%", height: "100%", objectFit: "contain", background: "#000" }}
    />
  );
}

export default function TrackPlayer() {
  const tracks = useTracks([
    { source: Track.Source.Camera, withPlaceholder: false },
    { source: Track.Source.ScreenShare, withPlaceholder: false },
  ]);

  const videoTracks = tracks.filter(t => t.publication?.track && !t.participant.isLocal);
  const localTracks = tracks.filter(t => t.publication?.track && t.participant.isLocal);
  const allTracks = [...localTracks, ...videoTracks];

  if (allTracks.length === 0) {
    return (
      <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", background: "#000" }}>
        <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.15em" }}>
          {localTracks.length === 0 ? "Waiting for stream..." : "Starting stream..."}
        </p>
      </div>
    );
  }

  return (
    <div style={{ width: "100%", height: "100%", background: "#000", position: "relative" }}>
      {allTracks.map((track, i) => (
        <div key={`${track.participant.identity}-${track.source}`} style={{
          position: allTracks.length === 1 ? "absolute" : "relative",
          inset: allTracks.length === 1 ? 0 : undefined,
          width: allTracks.length > 1 ? `${100 / allTracks.length}%` : "100%",
          height: "100%",
          display: "inline-block",
        }}>
          <VideoTrack track={track} />
          <div style={{ position: "absolute", bottom: 8, left: 8, fontSize: "0.6rem", color: "#fff", fontFamily: "monospace", background: "rgba(0,0,0,0.5)", padding: "2px 6px" }}>
            {track.participant.name || track.participant.identity}
          </div>
        </div>
      ))}
    </div>
  );
}
