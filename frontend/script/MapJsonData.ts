import * as fs from 'fs';
import path from 'path';
import logger from './logger';

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

  // Load form data
  logger.info('Reading form data JSON file...');
  const formFields: FormField[] = JSON.parse(
    fs.readFileSync(formFieldsPath, 'utf-8')
  );
  logger.info('Form data loaded successfully.');
  logger.debug(`Form data: ${JSON.stringify(formFields, null, 2)}`);

  // Load personal data
  logger.info('Reading personal data JSON file...');
  const data: { people: Person[] } = JSON.parse(
    fs.readFileSync(personalDataPath, 'utf-8')
  );
  logger.info('Personal data loaded successfully.');
  logger.debug(`Personal data: ${JSON.stringify(data, null, 2)}`);

  // Check if people data is valid
  if (!data.people || !Array.isArray(data.people) || data.people.length === 0) {
    throw new Error('The people data is missing or invalid.');
  }

  // Map function to update form fields with initial values from people data
  function updateInitialValues(
    formFields: FormField[],
    people: Person[]
  ): FormField[] {
    logger.info(
      'Mapping initial values with the first person in personal data...'
    );
    const person = people[0];

    return formFields.map((field) => {
      if (field.description === 'FamilyName') {
        logger.debug(`Updating FamilyName for field: ${field.field_name}`);
        return { ...field, initial_value: person.FamilyName };
      } else if (field.description === 'GivenName') {
        logger.debug(`Updating GivenName for field: ${field.field_name}`);
        return { ...field, initial_value: person.GivenName };
      } else {
        return field;
      }
    });
  }

  // Apply mapping to form fields
  const updatedFormFields: FormField[] = updateInitialValues(
    formFields,
    data.people
  );

  // Save the updated form fields to a JSON file
  logger.info('Saving updated form fields to JSON file...');
  fs.writeFileSync(
    outputFormFieldsPath,
    JSON.stringify(updatedFormFields, null, 2),
    'utf-8'
  );
  logger.info('Form fields have been updated successfully.');
} catch (error) {
  if (error instanceof Error) {
    logger.error(`Unexpected error during script execution: ${error.message}`);
    logger.error(error.stack || 'No stack trace available');
  } else {
    logger.error('An unknown error occurred.');
  }
}
