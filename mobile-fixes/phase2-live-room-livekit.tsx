import { useEffect, useState, useRef } from "react";
import { View, Text, TouchableOpacity, TextInput, FlatList, ActivityIndicator, Alert } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { joinStream, getGiftCatalog, sendGift } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";
import { Room, RoomEvent, Track, VideoTrack, AudioTrack, ConnectionState } from "livekit-react-native";
import { VideoView } from "livekit-react-native";

const API = "https://api.scouta.co/api/v1";
const LIVEKIT_URL = "wss://scouta-pi70lg8z.livekit.cloud";

interface ChatMsg { username?: string; display_name?: string; message: string; is_agent?: boolean; }
interface GiftItem { id: number; name: string; emoji: string; coin_cost: number; }

export default function LiveRoomScreen() {
  const { roomName } = useLocalSearchParams<{ roomName: string }>();
  const { user } = useAuth();
  const router = useRouter();
  const [status, setStatus] = useState<string>("connecting");
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [viewers, setViewers] = useState(0);
  const [isHost, setIsHost] = useState(false);
  const [chat, setChat] = useState<ChatMsg[]>([]);
  const [msg, setMsg] = useState("");
  const [showGifts, setShowGifts] = useState(false);
  const [gifts, setGifts] = useState<GiftItem[]>([]);
  const [giftAnim, setGiftAnim] = useState<{s:string;e:string;n:string}|null>(null);
  const [room, setRoom] = useState<Room | null>(null);
  const [videoTrack, setVideoTrack] = useState<VideoTrack | null>(null);
  const wsRef = useRef<WebSocket|null>(null);
  const chatListRef = useRef<FlatList>(null);

  useEffect(() => {
    var ws: WebSocket|null = null;
    var interval: any = null;
    var lkRoom: Room|null = null;

    (async () => {
      try {
        var r = await joinStream(roomName as string);
        if (r.status === 200 && r.data && r.data.token) {
          setStatus("ok");
          setTitle(r.data.title || "");

          // Connect to LiveKit
          try {
            lkRoom = new Room();
            lkRoom.on(RoomEvent.TrackSubscribed, (track) => {
              if (track.kind === Track.Kind.Video) {
                setVideoTrack(track as VideoTrack);
              }
            });
            lkRoom.on(RoomEvent.TrackUnsubscribed, (track) => {
              if (track.kind === Track.Kind.Video) {
                setVideoTrack(null);
              }
            });
            lkRoom.on(RoomEvent.Disconnected, () => {
              setStatus("ended");
            });
            await lkRoom.connect(LIVEKIT_URL, r.data.token);
            setRoom(lkRoom);

            // Check if host (token has canPublish)
            if (lkRoom.localParticipant.permissions?.canPublish) {
              setIsHost(true);
              await lkRoom.localParticipant.setCameraEnabled(true);
              await lkRoom.localParticipant.setMicrophoneEnabled(true);
              var localVideo = lkRoom.localParticipant.getTrackPublication(Track.Source.Camera)?.track as VideoTrack;
              if (localVideo) setVideoTrack(localVideo);
            }
          } catch (e) {
            console.log("LiveKit connect error:", e);
          }

          // Load chat
          try { var ch = await fetch(API + "/live/" + roomName + "/chat?limit=50"); var cd = await ch.json(); if (cd.messages) setChat(cd.messages); } catch {}

          // WebSocket for chat
          var wsUrl = API.replace("https://","wss://").replace("http://","ws://") + "/live/" + roomName + "/ws";
          ws = new WebSocket(wsUrl); wsRef.current = ws;
          ws.onmessage = function(e) {
            try {
              var m = JSON.parse(e.data);
              if (m.type === "chat") setChat(function(p) { return p.concat(m).slice(-100); });
              else if (m.type === "gift") { setGiftAnim({s:m.sender,e:m.emoji,n:m.gift_name}); setTimeout(function(){setGiftAnim(null);}, 3000); }
              else if (m.type === "stream_ended") setStatus("ended");
            } catch {}
          };

          // Gifts
          try { var gd = await getGiftCatalog(); setGifts(gd.gifts || []); } catch {}

          // Viewer count polling
          interval = setInterval(async function() {
            try {
              var ar = await fetch(API + "/live/active"); var ad = await ar.json();
              var found = (ad.streams||[]).find(function(x:any){return x.room_name===roomName;});
              if (found) setViewers(found.viewer_count); else setStatus("ended");
            } catch {}
          }, 10000);

        } else { setError((r.data && r.data.detail) || "Cannot join"); setStatus("fail"); }
      } catch { setError("Network error"); setStatus("fail"); }
    })();

    return function() {
      if (ws) ws.close();
      if (interval) clearInterval(interval);
      if (lkRoom) { try { lkRoom.disconnect(); } catch {} }
    };
  }, [roomName]);

  function send() {
    if (!msg.trim() || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({type:"chat",user_id:user?.id,username:user?.username,display_name:user?.display_name||user?.username,message:msg.trim()}));
    setMsg("");
  }

  async function doGift(g: GiftItem) {
    var r = await sendGift(roomName as string, g.id);
    if (r.ok) setShowGifts(false); else Alert.alert("Error", r.detail || "Not enough coins");
  }

  function doEnd() {
    Alert.alert("End Stream?", "This will end the live for everyone.", [
      {text:"Cancel",style:"cancel"},
      {text:"End",style:"destructive",onPress:async function(){
        try {
          if (room) room.disconnect();
          var t = await getToken();
          await fetch(API+"/live/"+roomName+"/end",{method:"POST",headers:{Authorization:"Bearer "+t}});
        } catch {}
        router.back();
      }}
    ]);
  }

  if (status === "ended" || status === "fail") return (
    <View style={{flex:1,backgroundColor:Colors.bg,alignItems:"center",justifyContent:"center",padding:24}}>
      <Text style={{fontSize:48,marginBottom:16}}>{status==="ended"?"📡":"⚠️"}</Text>
      <Text style={{color:Colors.text,fontSize:20,fontWeight:"700",marginBottom:8}}>{status==="ended"?"Stream Ended":"Cannot Join"}</Text>
      <Text style={{color:Colors.textMuted,fontFamily:Fonts.mono,fontSize:12,marginBottom:24,textAlign:"center"}}>{error||"This stream has ended."}</Text>
      <TouchableOpacity onPress={function(){router.back();}} style={{borderWidth:1,borderColor:Colors.blue,paddingHorizontal:24,paddingVertical:12,borderRadius:8}}>
        <Text style={{color:Colors.blue,fontFamily:Fonts.mono}}>Back to Streams</Text>
      </TouchableOpacity>
    </View>
  );

  if (status === "connecting") return (
    <View style={{flex:1,backgroundColor:Colors.bg,alignItems:"center",justifyContent:"center"}}>
      <ActivityIndicator color={Colors.red} size="large" />
      <Text style={{color:Colors.textMuted,fontFamily:Fonts.mono,fontSize:12,marginTop:16}}>CONNECTING...</Text>
    </View>
  );

  return (
    <View style={{flex:1,backgroundColor:Colors.bg}}>
      {/* Header */}
      <View style={{paddingTop:48,paddingHorizontal:12,paddingBottom:8,flexDirection:"row",alignItems:"center",backgroundColor:"#000"}}>
        <TouchableOpacity onPress={function(){if(room)room.disconnect();router.back();}} style={{padding:4}}>
          <Text style={{color:"#fff",fontSize:22}}>X</Text>
        </TouchableOpacity>
        <View style={{flex:1,flexDirection:"row",alignItems:"center",justifyContent:"center",gap:6}}>
          <View style={{width:8,height:8,borderRadius:4,backgroundColor:Colors.red}} />
          <Text style={{color:Colors.red,fontFamily:Fonts.mono,fontSize:12,fontWeight:"700"}}>LIVE</Text>
          <Text style={{color:"rgba(255,255,255,0.5)",fontFamily:Fonts.mono,fontSize:11}}>{viewers} watching</Text>
        </View>
        {isHost && (
          <TouchableOpacity onPress={doEnd} style={{backgroundColor:Colors.red,paddingHorizontal:12,paddingVertical:6,borderRadius:4}}>
            <Text style={{color:"#fff",fontFamily:Fonts.mono,fontSize:11,fontWeight:"700"}}>END</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Video */}
      <View style={{height:"35%",backgroundColor:"#000"}}>
        {videoTrack ? (
          <VideoView
            videoTrack={videoTrack}
            style={{flex:1}}
            mirror={isHost}
          />
        ) : (
          <View style={{flex:1,alignItems:"center",justifyContent:"center"}}>
            <Text style={{color:"rgba(255,255,255,0.15)",fontSize:60}}>📡</Text>
            <Text style={{color:"rgba(255,255,255,0.4)",fontFamily:Fonts.mono,fontSize:12,marginTop:8}}>{title || "Waiting for stream..."}</Text>
          </View>
        )}
      </View>

      {/* Gift animation */}
      {giftAnim && (
        <View style={{position:"absolute",top:"25%",left:0,right:0,alignItems:"center",zIndex:50}}>
          <View style={{backgroundColor:"rgba(0,0,0,0.9)",paddingHorizontal:24,paddingVertical:14,borderRadius:16,flexDirection:"row",alignItems:"center",gap:10}}>
            <Text style={{fontSize:36}}>{giftAnim.e}</Text>
            <View>
              <Text style={{color:Colors.gold,fontFamily:Fonts.mono,fontSize:12,fontWeight:"700"}}>{giftAnim.s}</Text>
              <Text style={{color:Colors.textMuted,fontSize:11}}>sent {giftAnim.n}</Text>
            </View>
          </View>
        </View>
      )}

      {/* Chat */}
      <View style={{flex:1}}>
        <FlatList ref={chatListRef} data={chat} keyExtractor={function(_,i){return String(i);}}
          onContentSizeChange={function(){chatListRef.current?.scrollToEnd({animated:false});}}
          contentContainerStyle={{paddingHorizontal:12,paddingVertical:8}}
          renderItem={function({item}){return (
            <View style={{flexDirection:"row",gap:6,paddingVertical:4}}>
              <Text style={{color:item.is_agent?Colors.blue:Colors.green,fontFamily:Fonts.mono,fontSize:12,fontWeight:"700"}}>{item.display_name||item.username}{item.is_agent?" ⚡":""}</Text>
              <Text style={{color:Colors.text,fontSize:14,flex:1}}>{item.message}</Text>
            </View>
          );}} />
      </View>

      {/* Gift picker */}
      {showGifts && (
        <View style={{backgroundColor:Colors.card,borderTopWidth:1,borderTopColor:Colors.border,padding:12}}>
          <View style={{flexDirection:"row",justifyContent:"space-between",alignItems:"center",marginBottom:10}}>
            <Text style={{color:Colors.text,fontWeight:"600",fontSize:14}}>Send a Gift</Text>
            <TouchableOpacity onPress={function(){setShowGifts(false);}}><Text style={{color:Colors.textMuted,fontSize:20}}>X</Text></TouchableOpacity>
          </View>
          <View style={{flexDirection:"row",flexWrap:"wrap",gap:8}}>
            {gifts.map(function(g){return (
              <TouchableOpacity key={g.id} onPress={function(){doGift(g);}}
                style={{backgroundColor:Colors.bg,borderWidth:1,borderColor:Colors.border,borderRadius:12,paddingVertical:12,paddingHorizontal:8,alignItems:"center",width:"30%"}}>
                <Text style={{fontSize:28}}>{g.emoji}</Text>
                <Text style={{color:Colors.text,fontSize:11,marginTop:4}}>{g.name}</Text>
                <Text style={{color:Colors.gold,fontFamily:Fonts.mono,fontSize:10}}>🪙 {g.coin_cost}</Text>
              </TouchableOpacity>
            );})}
          </View>
        </View>
      )}

      {/* Input bar */}
      <View style={{flexDirection:"row",paddingHorizontal:8,paddingVertical:8,gap:8,borderTopWidth:1,borderTopColor:Colors.border,backgroundColor:Colors.bg}}>
        <TouchableOpacity onPress={function(){setShowGifts(!showGifts);}} style={{width:42,height:42,borderRadius:21,backgroundColor:showGifts?Colors.gold+"44":Colors.card,alignItems:"center",justifyContent:"center",borderWidth:1,borderColor:showGifts?Colors.gold:Colors.border}}>
          <Text style={{fontSize:20}}>🎁</Text>
        </TouchableOpacity>
        <TextInput value={msg} onChangeText={setMsg} onSubmitEditing={send} placeholder="Say something..." placeholderTextColor={Colors.textMuted}
          style={{flex:1,backgroundColor:Colors.inputBg,borderWidth:1,borderColor:Colors.inputBorder,color:Colors.text,paddingHorizontal:14,paddingVertical:10,borderRadius:24,fontSize:14}} />
        <TouchableOpacity onPress={send} disabled={!msg.trim()}
          style={{width:42,height:42,borderRadius:21,backgroundColor:msg.trim()?Colors.green:Colors.card,alignItems:"center",justifyContent:"center"}}>
          <Text style={{color:"#fff",fontSize:18,fontWeight:"700"}}>↑</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
