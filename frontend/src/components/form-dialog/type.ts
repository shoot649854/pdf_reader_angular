export type PDFItemType = {
  title: string;
  subtitle: string;
  questions: PDFQuestionType[];
  fields: any[];
};

export type PDFQuestionType = {
  field_name: string;
  description: string;
  field_type: string;
  value: string;
  initial_value: string;
  options?: string[];
  need?: string[];
  required?: boolean;
};
