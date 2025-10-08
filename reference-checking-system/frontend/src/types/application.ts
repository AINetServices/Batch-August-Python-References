// src/types/application.ts
export interface Application {
  id: string
  user_id: string
  resume_url: string
  role_id: string
  organization_id: string
  extracted_data: any
  status: 'processing' | 'extracted' | 'approved' | 'sent' | 'completed'
  created_at: string
  updated_at: string
  roles?: { name: string }
  organizations?: { name: string }
}