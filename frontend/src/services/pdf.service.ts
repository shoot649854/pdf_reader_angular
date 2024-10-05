import { Injectable } from '@angular/core';
import { PDFDocument, rgb, StandardFonts, PDFPage } from 'pdf-lib';
import axios from 'axios';
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist';
import { environment } from '../environment/environment';

// Configure PDF.js worker
GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.14.305/pdf.worker.min.js';

@Injectable({
  providedIn: 'root',
})
export class PdfService {
  // private visionApiKey: string = process.env['GOOGLE_CLOUD_VISION_API_KEY'] || '';
  private visionApiKey: string = environment.visionApiKey;
  constructor() {}

  /**
   * Merge multiple PDF chunks into a single PDF and return as a Blob URL.
   */

  async mergePdfChunks(chunks: Uint8Array[]): Promise<string> {
    const mergedPdf = await PDFDocument.create();
    for (const chunk of chunks) {
      const pdf = await PDFDocument.load(chunk);
      const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
      copiedPages.forEach((page) => mergedPdf.addPage(page));
    }
    const mergedBytes = await mergedPdf.save();
    return URL.createObjectURL(new Blob([mergedBytes], { type: 'application/pdf' }));
  }

  /**
   * Split a PDF into chunks of specified page sizes.
   */
  async splitPdf(pdfBytes: Uint8Array, chunkSize = 5): Promise<Uint8Array[]> {
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const totalPages = pdfDoc.getPageCount();
    const chunks: Uint8Array[] = [];

    for (let i = 0; i < totalPages; i += chunkSize) {
      const newPdf = await PDFDocument.create();
      const end = Math.min(i + chunkSize, totalPages);
      const pageIndices = [];
      for (let j = i; j < end; j++) {
        pageIndices.push(j);
      }
      const copiedPages = await newPdf.copyPages(pdfDoc, pageIndices);
      copiedPages.forEach((page) => newPdf.addPage(page));
      chunks.push(await newPdf.save());
    }

    return chunks;
  }

  /**
   * Add fillable fields to a PDF based on detected text fields using OCR.
   */
  async addFillableFieldsToPdf(pdfBytes: Uint8Array): Promise<Uint8Array> {
    const images = await this.convertPdfToImages(pdfBytes);
    const detectedFields = await this.detectTextFields(images);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const form = pdfDoc.getForm();
    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

    for (const field of detectedFields) {
      const { pageNumber, description, boundingPoly } = field;

      const page = pdfDoc.getPages()[pageNumber - 1];
      const { xMin, yMin, xMax, yMax } = this.calculateBoundingBox(boundingPoly);

      const pdfCoordinates = this.mapImageToPdfCoordinates(
        boundingPoly,
        images[pageNumber - 1].width,
        images[pageNumber - 1].height,
        page.getSize().width,
        page.getSize().height,
      );

      if (description.toLowerCase().includes('agree')) {
        const checkbox = form.createCheckBox(description.replace(/\s+/g, '_'));
        checkbox.addToPage(page, {
          x: pdfCoordinates.xMin,
          y: pdfCoordinates.yMin,
          width: pdfCoordinates.width,
          height: pdfCoordinates.height,
        });
        checkbox.updateAppearances();
      } else {
        const textField = form.createTextField(description.replace(/\s+/g, '_'));
        textField.setText('');
        textField.addToPage(page, {
          x: pdfCoordinates.xMin,
          y: pdfCoordinates.yMin,
          width: pdfCoordinates.width,
          height: pdfCoordinates.height,
        });
        textField.updateAppearances(font);
      }
    }

    const modifiedPdfBytes = await pdfDoc.save();
    return modifiedPdfBytes;
  }

  /**
   * Convert PDF pages to images using PDF.js.
   * @param pdfBytes - The PDF as Uint8Array.
   * @returns An array of image data URLs.
   */
  private async convertPdfToImages(pdfBytes: Uint8Array): Promise<HTMLCanvasElement[]> {
    const loadingTask = getDocument({ data: pdfBytes });
    const pdf = await loadingTask.promise;
    const numPages = pdf.numPages;
    const images: HTMLCanvasElement[] = [];

    for (let pageNum = 1; pageNum <= numPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const viewport = page.getViewport({ scale: 2.0 }); // Adjust scale for better quality
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d') as CanvasRenderingContext2D;
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      const renderContext = {
        canvasContext: context,
        viewport: viewport,
      };

      await page.render(renderContext).promise;
      images.push(canvas);
    }

    return images;
  }

  /**
   * Perform OCR on images using Google Cloud Vision API.
   * @param canvases - Array of HTMLCanvasElements representing PDF pages.
   * @returns Array of detected text fields with positional data.
   */
  // private async detectTextFields(canvases: HTMLCanvasElement[]): Promise<DetectedField[]> {
  //   const detectedFields: DetectedField[] = [];
  //   for (let i = 0; i < canvases.length; i++) {
  //     const canvas = canvases[i];
  //     const imgData = canvas.toDataURL('image/png').split(',')[1]; // Get base64 string

  //     const requestPayload = {
  //       requests: [
  //         {
  //           image: {
  //             content: imgData,
  //           },
  //           features: [
  //             {
  //               type: 'TEXT_DETECTION',
  //               maxResults: 100,
  //             },
  //           ],
  //         },
  //       ],
  //     };

  //     try {
  //       const response = await axios.post(
  //         `https://vision.googleapis.com/v1/images:annotate?key=${this.visionApiKey}`,
  //         requestPayload,
  //         {
  //           headers: {
  //             'Content-Type': 'application/json',
  //           },
  //         },
  //       );

  //       const annotations = response.data.responses[0].textAnnotations;
  //       if (annotations) {
  //         for (let j = 1; j < annotations.length; j++) {
  //           const annotation = annotations[j];
  //           detectedFields.push({
  //             pageNumber: i + 1,
  //             description: annotation.description,
  //             boundingPoly: annotation.boundingPoly,
  //           });
  //         }
  //       }
  //     } catch (error) {
  //       console.error('Error during OCR:', error);
  //     }
  //   }

  //   return detectedFields;
  // }
  private async detectTextFields(canvases: HTMLCanvasElement[]): Promise<DetectedField[]> {
    const detectedFields: DetectedField[] = [];
    for (let i = 0; i < canvases.length; i++) {
      const canvas = canvases[i];
      const imgData = canvas.toDataURL('image/png').split(',')[1]; // Get base64 string

      const requestPayload = {
        imageBase64: imgData,
      };

      try {
        const response = await axios.post('http://localhost:5001/api/vision/ocr', requestPayload, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const annotations = response.data.textAnnotations;
        if (annotations) {
          for (let j = 0; j < annotations.length; j++) {
            // Iterate through all annotations, including the first
            const annotation = annotations[j];
            detectedFields.push({
              pageNumber: i + 1,
              description: annotation.text, // Use 'text' instead of 'description'
              boundingPoly: annotation.boundingBox, // Use 'boundingBox' instead of 'boundingPoly'
            });
          }
        }
      } catch (error) {
        console.error('Error during OCR:', error);
      }
    }

    return detectedFields;
  }

  /**
   * Calculate bounding box coordinates from Vision API's boundingPoly.
   * @param boundingPoly - The bounding polygon from Vision API.
   * @returns An object with min and max coordinates.
   */
  private calculateBoundingBox(boundingPoly: any): BoundingBox {
    const vertices = boundingPoly.vertices;
    const xValues = vertices.map((vertex: any) => vertex.x || 0);
    const yValues = vertices.map((vertex: any) => vertex.y || 0);
    return {
      xMin: Math.min(...xValues),
      yMin: Math.min(...yValues),
      xMax: Math.max(...xValues),
      yMax: Math.max(...yValues),
    };
  }

  /**
   * Map image coordinates to PDF coordinates.
   * @param boundingPoly - The bounding polygon from Vision API.
   * @param imgWidth - Width of the image.
   * @param imgHeight - Height of the image.
   * @param pdfWidth - Width of the PDF page.
   * @param pdfHeight - Height of the PDF page.
   * @returns An object with mapped PDF coordinates.
   */
  private mapImageToPdfCoordinates(
    boundingPoly: any,
    imgWidth: number,
    imgHeight: number,
    pdfWidth: number,
    pdfHeight: number,
  ): MappedCoordinates {
    const box = this.calculateBoundingBox(boundingPoly);

    // Calculate scale ratios
    const xScale = pdfWidth / imgWidth;
    const yScale = pdfHeight / imgHeight;

    // Map coordinates
    const xMin = box.xMin * xScale;
    const yMin = pdfHeight - box.yMax * yScale; // PDF origin is bottom-left
    const width = (box.xMax - box.xMin) * xScale;
    const height = (box.yMax - box.yMin) * yScale;

    return { xMin, yMin, width, height };
  }
}

/**
 * Interface for detected text fields.
 */
interface DetectedField {
  pageNumber: number;
  description: string;
  boundingPoly: any;
}

/**
 * Interface for bounding box coordinates.
 */
interface BoundingBox {
  xMin: number;
  yMin: number;
  xMax: number;
  yMax: number;
}

/**
 * Interface for mapped PDF coordinates.
 */
interface MappedCoordinates {
  xMin: number;
  yMin: number;
  width: number;
  height: number;
}
