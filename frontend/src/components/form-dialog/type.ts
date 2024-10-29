export type PDFFieldType = {
  field_name: string;
  description: string;
  field_type: string;
  value: string;
  initial_value: string;
  options?: string[];
  need?: string[];
  required?: boolean;
};
