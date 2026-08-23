import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client'

interface Story {
  id: string
  title: string
  is_public: boolean
  created_at: string
}

export default function Dashboard() {
  const [stories, setStories] = useState<Story[]>([])
  const [title, setTitle] = useState('')
  const [isPublic, setIsPublic] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    client.get('/stories/stories').then(res => setStories(res.data))
  }, [])

  const createStory = async () => {
    const res = await client.post('/stories/stories', { title, is_public: isPublic })
    setStories([...stories, res.data])
    setTitle('')
  }

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">PlotTree</h1>
        <button onClick={logout} className="text-sm text-gray-500 underline">logout</button>
      </div>

      <div className="bg-white border rounded-lg p-4 mb-8">
        <h2 className="font-semibold mb-3">start a new story</h2>
        <input
          className="w-full border p-2 rounded mb-3"
          placeholder="story title"
          value={title}
          onChange={e => setTitle(e.target.value)}
        />
        <div className="flex items-center gap-2 mb-3">
          <input
            type="checkbox"
            checked={isPublic}
            onChange={e => setIsPublic(e.target.checked)}
          />
          <label className="text-sm">public story</label>
        </div>
        <button
          className="bg-black text-white px-4 py-2 rounded"
          onClick={createStory}
        >
          create
        </button>
      </div>

      <h2 className="font-semibold mb-4">public stories</h2>
      <div className="space-y-3">
        {stories.map(story => (
          <div
            key={story.id}
            className="bg-white border rounded-lg p-4 cursor-pointer hover:shadow"
            onClick={() => navigate(`/stories/${story.id}`)}
          >
            <h3 className="font-medium">{story.title}</h3>
            <p className="text-sm text-gray-500">{story.is_public ? 'public' : 'private'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}