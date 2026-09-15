import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AppProvider } from './AppContext'
import { Layout } from './components/Layout'
import { RequireAuth } from './components/RequireAuth'
import { AssistantDetailPage, AssistantsPage } from './pages/Assistants'
import { AssistantGroupDetailPage, AssistantGroupsPage } from './pages/AssistantGroups'
import { ContentDetailPage, ContentPage } from './pages/Content'
import { HomePage } from './pages/Home'
import { MessagesPage } from './pages/Messages'
import { NotFoundPage } from './pages/NotFound'
import { PostDetailPage, PostsPage } from './pages/Posts'
import { SchemasPage } from './pages/Schemas'
import { SettingsPage } from './pages/Settings'
import { ThreadDetailPage, ThreadsPage } from './pages/Threads'

/** Wrap an authoring screen in the sign-in gate. */
function guarded(element: React.ReactElement) {
  return <RequireAuth>{element}</RequireAuth>
}

export function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="content" element={guarded(<ContentPage />)} />
            <Route path="content/:id" element={guarded(<ContentDetailPage />)} />
            <Route path="threads" element={guarded(<ThreadsPage />)} />
            <Route path="threads/:id" element={guarded(<ThreadDetailPage />)} />
            <Route path="messages" element={guarded(<MessagesPage />)} />
            <Route path="posts" element={guarded(<PostsPage />)} />
            <Route path="posts/:id" element={guarded(<PostDetailPage />)} />
            <Route path="assistants" element={guarded(<AssistantsPage />)} />
            <Route path="assistants/new" element={guarded(<AssistantDetailPage />)} />
            <Route path="assistants/:id" element={guarded(<AssistantDetailPage />)} />
            <Route path="assistant-groups" element={guarded(<AssistantGroupsPage />)} />
            <Route path="assistant-groups/new" element={guarded(<AssistantGroupDetailPage />)} />
            <Route path="assistant-groups/:id" element={guarded(<AssistantGroupDetailPage />)} />
            <Route path="schemas" element={guarded(<SchemasPage />)} />
            <Route path="settings" element={guarded(<SettingsPage />)} />
            {/* The old Django URLs, kept working as redirects. */}
            <Route path="assistant-groups/edit/:id" element={<Navigate to="/assistant-groups" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  )
}
