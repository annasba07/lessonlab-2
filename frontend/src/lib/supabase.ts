import { createBrowserClient } from '@supabase/ssr'

// Temporarily disable Supabase client to test if env vars are causing issues
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://placeholder'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder'

export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey)