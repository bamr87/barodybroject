/** One place that knows every API path and its payload shape. */

import { api, listAll } from './client'
import type {
  AIModel,
  Assistant,
  AssistantGroup,
  AuthState,
  ContentDetail,
  GenerateResponse,
  JSONSchemaRecord,
  Message,
  Post,
  PostVersion,
  Provider,
  SiteInfo,
  SyncReport,
  Thread,
} from './types'

export const auth = {
  me: () => api.get<AuthState>('/api/auth/me/'),
}

export const site = {
  info: () => api.get<SiteInfo>('/api/site/'),
}

export const providers = {
  list: () => api.get<Provider[]>('/api/providers/'),
  get: (slug: string) => api.get<Provider>(`/api/providers/${slug}/`),
  models: (slug: string) =>
    api.get<{ id: string; provider: string; display_name: string; description: string }[]>(
      `/api/providers/${slug}/models/`,
    ),
  sync: (slug: string) => api.post<SyncReport>(`/api/providers/${slug}/sync/`),
  test: (slug: string) => api.post<{ ok: boolean; model: string; text: string }>(`/api/providers/${slug}/test/`),
  saveConfig: (slug: string, body: Record<string, unknown>) =>
    api.patch<Provider>(`/api/providers/${slug}/config/`, body),
  setDefault: (slug: string) => api.post<Provider>(`/api/providers/${slug}/set-default/`),
}

export const aiModels = {
  list: (params?: { provider?: string; active?: string }) =>
    listAll<AIModel>('/api/ai-models/', { params }),
}

export const assistants = {
  list: () => listAll<Assistant>('/api/assistants/'),
  get: (id: string) => api.get<Assistant>(`/api/assistants/${id}/`),
  create: (body: Partial<Assistant>) => api.post<Assistant>('/api/assistants/', body),
  update: (id: string, body: Partial<Assistant>) => api.patch<Assistant>(`/api/assistants/${id}/`, body),
  remove: (id: string) => api.delete<void>(`/api/assistants/${id}/`),
}

export const assistantGroups = {
  list: () => listAll<AssistantGroup>('/api/assistant-groups/'),
  get: (id: number) => api.get<AssistantGroup>(`/api/assistant-groups/${id}/`),
  create: (body: Partial<AssistantGroup>) => api.post<AssistantGroup>('/api/assistant-groups/', body),
  update: (id: number, body: Partial<AssistantGroup>) =>
    api.patch<AssistantGroup>(`/api/assistant-groups/${id}/`, body),
  remove: (id: number) => api.delete<void>(`/api/assistant-groups/${id}/`),
}

export const schemas = {
  list: () => listAll<JSONSchemaRecord>('/api/json-schemas/'),
  get: (id: number) => api.get<JSONSchemaRecord>(`/api/json-schemas/${id}/`),
  create: (body: Partial<JSONSchemaRecord>) => api.post<JSONSchemaRecord>('/api/json-schemas/', body),
  update: (id: number, body: Partial<JSONSchemaRecord>) =>
    api.patch<JSONSchemaRecord>(`/api/json-schemas/${id}/`, body),
  remove: (id: number) => api.delete<void>(`/api/json-schemas/${id}/`),
  bundled: () => api.get<{ name: string; schema: Record<string, unknown> }[]>('/api/json-schemas/bundled/'),
}

export const content = {
  list: () => listAll<ContentDetail>('/api/content-details/'),
  get: (id: number) => api.get<ContentDetail>(`/api/content-details/${id}/`),
  create: (body: Record<string, unknown>) => api.post<ContentDetail>('/api/content-details/', body),
  update: (id: number, body: Record<string, unknown>) =>
    api.patch<ContentDetail>(`/api/content-details/${id}/`, body),
  remove: (id: number) => api.delete<void>(`/api/content-details/${id}/`),
  generate: (id: number, provider?: string) =>
    api.post<GenerateResponse>(`/api/content-details/${id}/generate/`, { provider }),
  createThread: (id: number, body: { assistant_group?: number | null; name?: string }) =>
    api.post<Thread>(`/api/content-details/${id}/create-thread/`, body),
}

export const threads = {
  list: () => listAll<Thread>('/api/threads/'),
  get: (id: string) => api.get<Thread>(`/api/threads/${id}/`),
  update: (id: string, body: Partial<Thread>) => api.patch<Thread>(`/api/threads/${id}/`, body),
  remove: (id: string) => api.delete<void>(`/api/threads/${id}/`),
  addMessage: (id: string, text: string, assistant?: string | null) =>
    api.post<Thread>(`/api/threads/${id}/add-message/`, { text, assistant }),
  run: (id: string, assistant: string, provider?: string) =>
    api.post<{ message: Message; thread: Thread }>(`/api/threads/${id}/run/`, { assistant, provider }),
  runGroup: (id: string, assistantGroup?: number | null, provider?: string) =>
    api.post<{ messages: Message[]; thread: Thread }>(`/api/threads/${id}/run-group/`, {
      assistant_group: assistantGroup,
      provider,
    }),
}

export const messages = {
  list: (threadId?: string) => listAll<Message>('/api/messages/', { params: { thread: threadId } }),
  get: (id: string) => api.get<Message>(`/api/messages/${id}/`),
  remove: (id: string) => api.delete<void>(`/api/messages/${id}/`),
  assign: (id: string, assistant: string | null) =>
    api.post<Message>(`/api/messages/${id}/assign/`, { assistant }),
  run: (id: string, assistant?: string, provider?: string) =>
    api.post<Message>(`/api/messages/${id}/run/`, { assistant, provider }),
  createContent: (id: string) => api.post<ContentDetail>(`/api/messages/${id}/create-content/`),
  createPost: (id: string) => api.post<Post>(`/api/messages/${id}/create-post/`),
}

export const posts = {
  list: () => listAll<Post>('/api/posts/'),
  get: (id: number) => api.get<Post>(`/api/posts/${id}/`),
  update: (id: number, body: Record<string, unknown>) => api.patch<Post>(`/api/posts/${id}/`, body),
  remove: (id: number) => api.delete<void>(`/api/posts/${id}/`),
  publish: (id: number) =>
    api.post<{ url: string; version: PostVersion; post: Post }>(`/api/posts/${id}/publish/`),
  versions: (id: number) => api.get<PostVersion[]>(`/api/posts/${id}/versions/`),
  render: (id: number) =>
    api.get<{ filename: string; frontmatter: string; document: string }>(`/api/posts/${id}/render/`),
}
