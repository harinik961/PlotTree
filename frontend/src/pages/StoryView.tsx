import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ReactFlow} from '@xyflow/react'
import type { Edge, Node } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import client from '../api/client'

interface Branch {
  id: string
  title: string
  parent_branch: string | null
  is_canonical: boolean
  voting_ends_at: string | null
}

export default function StoryView() {
  const { storyId } = useParams()
  const navigate = useNavigate()
  const [branches, setBranches] = useState<Branch[]>([])
  const [title, setTitle] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [selectedParent, setSelectedParent] = useState<string | null>(null)

  useEffect(() => {
    client.get(`/stories/stories/${storyId}`).then(res => {
      // fetch branches for this story
    })
    client.get(`/stories/stories/${storyId}/branches`).then(res => {
      setBranches(res.data)
    })
  }, [storyId])

  // convert branches to react-flow nodes and edges
  const nodes: Node[] = branches.map((branch, index) => ({
    id: branch.id,
    position: { x: index * 200, y: branch.parent_branch ? 200 : 0 },
    data: {
      label: (
        <div className="text-center">
          <p className="font-medium text-sm">{branch.title}</p>
          {branch.is_canonical && (
            <span className="text-xs text-green-600">canonical</span>
          )}
        </div>
      )
    },
    style: {
      background: branch.is_canonical ? '#f0fdf4' : '#fff',
      border: branch.is_canonical ? '2px solid #16a34a' : '1px solid #e5e7eb',
      borderRadius: 8,
      padding: 10,
      width: 160,
    }
  }))

  const edges: Edge[] = branches
    .filter(b => b.parent_branch)
    .map(b => ({
      id: `${b.parent_branch}-${b.id}`,
      source: b.parent_branch!,
      target: b.id,
      type: 'smoothstep',
    }))

  const createBranch = async () => {
    const res = await client.post(`/stories/stories/${storyId}/branches`, {
      title,
      parent_branch_id: selectedParent
    })
    setBranches([...branches, res.data])
    setTitle('')
    setShowCreate(false)
  }

  return (
    <div className="h-screen flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <button
          onClick={() => navigate('/dashboard')}
          className="text-sm text-gray-500 underline"
        >
          ← back
        </button>
        <h1 className="font-bold">story branches</h1>
        <button
          className="bg-black text-white px-3 py-1 rounded text-sm"
          onClick={() => setShowCreate(true)}
        >
          + branch
        </button>
      </div>

      {showCreate && (
        <div className="p-4 border-b bg-gray-50">
          <h2 className="font-semibold mb-3">create a branch</h2>
          <input
            className="w-full border p-2 rounded mb-3"
            placeholder="branch title"
            value={title}
            onChange={e => setTitle(e.target.value)}
          />
          <select
            className="w-full border p-2 rounded mb-3"
            onChange={e => setSelectedParent(e.target.value || null)}
          >
            <option value="">no parent (root branch)</option>
            {branches.map(b => (
              <option key={b.id} value={b.id}>{b.title}</option>
            ))}
          </select>
          <div className="flex gap-2">
            <button
              className="bg-black text-white px-4 py-2 rounded"
              onClick={createBranch}
            >
              create
            </button>
            <button
              className="border px-4 py-2 rounded"
              onClick={() => setShowCreate(false)}
            >
              cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={(_, node) => navigate(`/branches/${node.id}`)}
          fitView
        />
      </div>

      <div className="p-4 border-t text-xs text-gray-400 text-center">
        click a branch to open it — green = canonical path
      </div>
    </div>
  )
}