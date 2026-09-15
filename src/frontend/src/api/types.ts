/**
 * Shapes returned by the Django REST API (parodynews/api/serializers.py).
 * Keep these in step with the serializers; the app has no other contract.
 */

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
}

export interface AuthState {
  authenticated: boolean
  user: User | null
  csrf_token: string
  login_url: string
  logout_url: string
  signup_url: string
  profile_url: string | null
}

export interface IssueTemplate {
  filename: string
  name: string
}

export interface PoweredBy {
  id: number
  name: string
  icon: string
  url: string
}

export interface SiteInfo {
  name: string
  version: string
  default_provider: string
  providers: string[]
  publications_url: string
  github_issue_repo: string
  issue_templates: IssueTemplate[]
  powered_by: PoweredBy[]
  admin_url: string
}

export interface AIModel {
  id: number
  provider: string
  model_id: string
  display_name: string
  description: string
  is_active: boolean
  label: string
  created_at: string
  updated_at: string
}

export interface ProviderConfig {
  id: number
  provider: string
  display_name: string
  has_credential: boolean
  base_url: string
  organization_id: string
  project_id: string
  default_model: string
  is_default: boolean
  is_enabled: boolean
  extra: Record<string, unknown>
}

export interface Provider {
  slug: string
  display_name: string
  description: string
  default_model: string
  configured: boolean
  credential_source: string
  credential_env_vars: string[]
  model_env_var: string
  supports_model_discovery: boolean
  base_url: string
  enabled: boolean
  is_default: boolean
  config: ProviderConfig | null
  catalogue_count: number
}

export interface JSONSchemaRecord {
  id: number
  name: string
  description: string
  schema: Record<string, unknown>
}

export interface AssistantGroupSummary {
  id: number
  name: string
}

export interface Assistant {
  id: string
  name: string
  description: string
  instructions: string
  prompt: string
  model: number | null
  model_detail: AIModel | null
  provider: string
  remote_id: string
  json_schema: number | null
  json_schema_name: string
  temperature: number | null
  top_p: number | null
  tools: unknown[]
  metadata: Record<string, unknown>
  response_format: Record<string, unknown>
  groups: AssistantGroupSummary[]
  created_at: string
}

export interface GroupMembership {
  id?: number
  assistant: string | null
  assistant_name?: string
  position: number
}

export interface AssistantGroup {
  id: number
  name: string
  group_type: string
  sequence: number
  is_active: boolean
  priority: number
  created_at: string
  memberships: GroupMembership[]
}

export interface ContentItem {
  id: number
  detail: number
  line_number: number
  content_type: string
  content_text: string
  assistant: string | null
  assistant_name: string
  prompt: string
}

export interface ContentDetail {
  id: number
  title: string
  description: string
  author: string
  published_at: string
  slug: string
  keywords: string[]
  user: User | null
  items: ContentItem[]
}

export interface Message {
  id: string
  thread: string | null
  thread_name: string
  role: 'user' | 'assistant' | 'system'
  contentitem: number | null
  content_text: string
  assistant: string | null
  assistant_name: string
  status: string
  run_id: string | null
  provider: string
  model_id: string
  remote_id: string
  usage: Record<string, unknown>
  error: string
  created_at: string
}

export interface Thread {
  id: string
  name: string
  description: string
  assistant_group: number | null
  assistant_group_name: string
  provider: string
  remote_id: string
  user: User | null
  message_count: number
  created_at: string
  messages?: Message[]
}

export interface PostFrontMatter {
  title: string
  description: string
  author: string
  published_at: string
  slug: string
}

export interface Post {
  id: number
  content_detail: number | null
  content_detail_title: string
  thread: string | null
  message: string | null
  assistant: string | null
  assistant_name: string
  post_content: string
  filename: string
  status: string
  front_matter: PostFrontMatter | null
  version_count: number
  user: User | null
  created_at: string
  updated_at: string
}

export interface PostVersion {
  id: number
  post: number
  version_number: number
  content: string
  frontmatter: string
  created_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface GenerationUsage {
  input_tokens?: number
  output_tokens?: number
  cost_usd?: number | null
  [key: string]: unknown
}

export interface GenerateResponse {
  content_detail: ContentDetail
  provider: string
  model: string
  usage: GenerationUsage
  content_text: string
  detail: Record<string, unknown> | null
  warnings: string[]
}

export interface SyncReport {
  provider: string
  created: string[]
  updated: string[]
  total: number
}
