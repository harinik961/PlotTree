import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import client from '../api/client'

interface Sentence {
  id: string
  content: string
  author_id: string
  created_at: string
}

interface PresenceUser {
  user_id: string
}
interface StorySegment {
  branch_id: string
  branch_title: string
  sentences: Sentence[]
}


export default function BranchView() {
  const { branchId } = useParams()
  const navigate = useNavigate()
  const [sentences, setSentences] = useState<Sentence[]>([])
  const [input, setInput] = useState('')
  const [presence, setPresence] = useState<string[]>([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const [segments, setSegments] = useState<StorySegment[]>([])


  // get current user id from token
  const token = localStorage.getItem('token')
  const userId = token ? JSON.parse(atob(token.split('.')[1])).sub : null

  useEffect(() => {
    // load full story (ancestor branches + this branch, in order)
    client.get(`/sentences/${branchId}/full-story`).then(res => {
      setSegments(res.data)
      const allSentences = res.data.flatMap((seg: StorySegment) => seg.sentences)
      setSentences(allSentences)
    })

    // connect to websocket
    const ws = new WebSocket(`ws://localhost:8000/ws/${branchId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      // announce presence
      ws.send(JSON.stringify({
        type: 'join',
        user_id: userId
      }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'new_sentence') {
        const newSentence = {
          id: data.id,
          content: data.content,
          author_id: data.author_id,
          created_at: new Date().toISOString()
        }
        setSentences(prev => [...prev, newSentence])
        setSegments(prev => {
          if (prev.length === 0) {
            return [{ branch_id: branchId!, branch_title: '', sentences: [newSentence] }]
          }
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            sentences: [...updated[updated.length - 1].sentences, newSentence]
          }
          return updated
        })
      }

      if (data.type === 'presence_update') {
        setPresence(data.users)
      }

      if (data.type === 'user_left') {
        setPresence(prev => prev.filter(u => u !== data.user_id))
      }
    }

    ws.onclose = () => setConnected(false)

    return () => {
      ws.close()
    }
  }, [branchId])

  // scroll to bottom when new sentence appears
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [sentences])

  const sendSentence = () => {
    if (!input.trim() || !wsRef.current) return
    wsRef.current.send(JSON.stringify({
      type: 'new_sentence',
      content: input,
      author_id: userId
    }))
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendSentence()
    }
  }

  return (
    <div className="h-screen flex flex-col">
      {/* header */}
      <div className="flex items-center justify-between p-4 border-b">
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-gray-500 underline"
        >
          ← back
        </button>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-300'}`} />
          <span className="text-xs text-gray-500">
            {connected ? 'live' : 'connecting...'}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {presence.slice(0, 3).map((u, i) => (
            <div
              key={i}
              className="w-7 h-7 rounded-full bg-gray-800 flex items-center justify-center text-white text-xs"
            >
              {u.slice(0, 2)}
            </div>
          ))}
          {presence.length > 3 && (
            <span className="text-xs text-gray-500">+{presence.length - 3}</span>
          )}
        </div>
      </div>

      {/* sentences */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {segments.length === 0 && (
          <p className="text-gray-400 text-center mt-20">
            no sentences yet — be the first to write
          </p>
        )}
        {segments.map((segment, i) => (
          <div key={segment.branch_id}>
            {i > 0 && (
              <div className="text-center text-xs text-gray-400 my-4">
                ↳ forked into "{segment.branch_title}"
              </div>
            )}
            {segment.sentences.map(sentence => (
              <div
                key={sentence.id}
                className={`flex ${sentence.author_id === userId ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-lg p-3 rounded-lg ${
                    sentence.author_id === userId
                      ? 'bg-black text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{sentence.content}</p>
                  <p className="text-xs mt-1 text-gray-400">
                    {sentence.author_id === userId ? 'you' : sentence.author_id.slice(0, 8)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <textarea
            className="flex-1 border rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-black"
            placeholder="add to the story... (enter to send)"
            rows={2}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="bg-black text-white px-4 rounded-lg text-sm"
            onClick={sendSentence}
          >
            send
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1">press enter to send</p>
      </div>
    </div>
  )
}