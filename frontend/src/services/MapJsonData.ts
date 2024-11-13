import * as fs from 'fs';
import path from 'path';

interface FormField {
  field_name: string;
  description: string;
  field_type: string;
  initial_value: string;
  page_number: number;
  options?: string[];
  need?: string[];
}

interface Person {
  FamilyName: string;
  GivenName: string;
  Age?: number;
  Address?: {
    Street: string;
    City: string;
    State?: string;
    ZipCode?: string;
  };
}

try {
  const formFieldsPath = path.resolve(__dirname, './src/assets/form_data.json');
  const personalDataPath = path.resolve(
    __dirname,
    './src/assets/personal_data.json'
  );
  const outputFormFieldsPath = path.resolve(
    __dirname,
    './src/assets/formFields.json'
  );

  const formFields: FormField[] = JSON.parse(
    fs.readFileSync(formFieldsPath, 'utf-8')
  );

  const data: { people: Person[] } = JSON.parse(
    fs.readFileSync(personalDataPath, 'utf-8')
  );

  if (!data.people || !Array.isArray(data.people) || data.people.length === 0) {
    throw new Error('The people data is missing or invalid.');
  }

  function updateInitialValues(
    formFields: FormField[],
    people: Person[]
  ): FormField[] {
    const person = people[0];

    return formFields.map((field) => {
      if (field.description === 'FamilyName') {
        return { ...field, initial_value: person.FamilyName };
      } else if (field.description === 'GivenName') {
        return { ...field, initial_value: person.GivenName };
      } else {
        return field;
      }
    });
  }

  const updatedFormFields: FormField[] = updateInitialValues(
    formFields,
    data.people
  );

  fs.writeFileSync(
    outputFormFieldsPath,
    JSON.stringify(updatedFormFields, null, 2),
    'utf-8'
  );
} catch (error) {
  if (error instanceof Error) {
  } else {
  }
}
