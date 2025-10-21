import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      applications: {
        Row: {
          id: string
          user_id: string
          resume_url: string
          role: string
          organization: string
          extracted_data: Json
          status: 'processing' | 'extracted' | 'approved' | 'sent' | 'completed'
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          resume_url: string
          role: string
          organization: string
          extracted_data?: Json
          status?: 'processing' | 'extracted' | 'approved' | 'sent' | 'completed'
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          resume_url?: string
          role?: string
          organization?: string
          extracted_data?: Json
          status?: 'processing' | 'extracted' | 'approved' | 'sent' | 'completed'
          created_at?: string
          updated_at?: string
        }
      }
      questions: {
        Row: {
          id: string
          role: string
          organization: string
          questions: Json
          created_at: string
        }
        Insert: {
          id?: string
          role: string
          organization: string
          questions: Json
          created_at?: string
        }
        Update: {
          id?: string
          role?: string
          organization?: string
          questions?: Json
          created_at?: string
        }
      }
      references: {
        Row: {
          id: string
          application_id: string
          name: string
          email: string
          company: string
          relationship: string
          years_worked: string
          questions_sent: Json
          responses: Json
          status: 'pending' | 'sent' | 'responded' | 'overdue'
          created_at: string
        }
        Insert: {
          id?: string
          application_id: string
          name: string
          email: string
          company: string
          relationship: string
          years_worked: string
          questions_sent?: Json
          responses?: Json
          status?: 'pending' | 'sent' | 'responded' | 'overdue'
          created_at?: string
        }
        Update: {
          id?: string
          application_id?: string
          name?: string
          email?: string
          company?: string
          relationship?: string
          years_worked?: string
          questions_sent?: Json
          responses?: Json
          status?: 'pending' | 'sent' | 'responded' | 'overdue'
          created_at?: string
        }
      }
    }
  }
}