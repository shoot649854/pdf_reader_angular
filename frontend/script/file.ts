import { getDocument } from 'pdfjs-dist';

async function logPdfFieldNames(pdfUrl: string): Promise<void> {
  try {
    const loadingTask = getDocument(pdfUrl);
    const pdfDocument = await loadingTask.promise;
    const numPages = pdfDocument.numPages;

    for (let i = 1; i <= numPages; i++) {
      const page = await pdfDocument.getPage(i);
      const annotations = await page.getAnnotations();

      annotations.forEach((annotation) => {
        if (annotation.fieldName) {
          console.log(`Field name: ${annotation.fieldName}`);
        }
      });
    }
  } catch (error) {
    console.error('Error loading PDF fields:', error);
  }
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Please provide the PDF URL as a CLI argument.');
    process.exit(1);
  }

  const pdfUrl = args[0];
  await logPdfFieldNames(pdfUrl);
}

main();
