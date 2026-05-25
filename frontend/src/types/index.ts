export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  firm_id: number;
  email: string;
  full_name: string;
  role: string;
}

export interface FirmUser {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: string;
  firm_id: number;
}

export interface Firm {
  id: number;
  name: string;
  legal_name: string | null;
  email: string | null;
  country: string;
  city: string | null;
}

export interface Client {
  id: number;
  firm_id: number;
  name: string;
  legal_name: string | null;
  registration_number: string | null;
  vat_number: string | null;
  industry: string | null;
  year_end_month: number;
  year_end_day: number;
  currency: string;
  contact_name: string | null;
  contact_email: string | null;
  is_active: boolean;
  created_at: string;
  engagement_count: number;
}

export interface Engagement {
  id: number;
  client_id: number;
  firm_id: number;
  year: number;
  period_start: string;
  period_end: string;
  comparative_year: number | null;
  status: 'DRAFT' | 'IN_PROGRESS' | 'REVIEW' | 'COMPLETE';
  reporting_standard: 'IFRS' | 'IFRS_SME';
  currency: string;
  preparer_id: number | null;
  reviewer_id: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  client_name?: string;
}

export interface TrialBalance {
  id: number;
  engagement_id: number;
  filename: string;
  is_comparative: boolean;
  status: 'PENDING' | 'PROCESSING' | 'PROCESSED' | 'ERROR';
  row_count: number;
  mapped_count: number;
  uploaded_at: string;
  processed_at: string | null;
  error_message: string | null;
  lines: TBLine[];
}

export interface TBLine {
  id: number;
  account_code: string | null;
  account_name: string;
  debit: string;
  credit: string;
  balance: string;
  is_comparative: boolean;
  ifrs_category: string | null;
  ifrs_subcategory: string | null;
  normal_balance: string | null;
  mapping_confidence: string | null;
  mapping_explanation: string | null;
  is_manually_mapped: boolean;
  is_excluded: boolean;
}

export interface StatementLine {
  id: number;
  section: string | null;
  subsection: string | null;
  label: string;
  current_amount: string | null;
  comparative_amount: string | null;
  note_reference: string | null;
  indent_level: number;
  is_header: boolean;
  is_subtotal: boolean;
  is_total: boolean;
  is_bold: boolean;
  order: number;
}

export interface FinancialStatement {
  id: number;
  engagement_id: number;
  statement_type: 'SFP' | 'PL' | 'CASH_FLOW' | 'EQUITY';
  version: number;
  is_approved: boolean;
  approved_at: string | null;
  generated_at: string;
  lines: StatementLine[];
}

export interface DisclosureNote {
  id: number;
  engagement_id: number;
  note_type: string;
  note_number: number | null;
  title: string;
  content: string | null;
  is_ai_generated: boolean;
  is_approved: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface ValidationResult {
  id: number;
  engagement_id: number;
  check_type: string;
  severity: 'ERROR' | 'WARNING' | 'INFO';
  message: string;
  details: string | null;
  is_resolved: boolean;
  resolved_at: string | null;
  created_at: string;
}

export interface ValidationSummary {
  total: number;
  errors: number;
  warnings: number;
  info: number;
  unresolved: number;
  results: ValidationResult[];
}
