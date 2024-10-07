"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var pdf_lib_1 = require("pdf-lib");
var fs = require("fs");
function fillPdfForm() {
    return __awaiter(this, void 0, void 0, function () {
        var formUrl, formPdfBytes, pdfDoc, form_1, fields, formFieldData_1, jsonData, pdfBytes, error_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 3, , 4]);
                    formUrl = 'src/assets/forms/i-140copy-decrypted.pdf';
                    formPdfBytes = fs.readFileSync(formUrl);
                    console.log('Loading PDF document...');
                    return [4 /*yield*/, pdf_lib_1.PDFDocument.load(formPdfBytes, {
                            ignoreEncryption: true,
                            throwOnInvalidObject: false
                        })];
                case 1:
                    pdfDoc = _a.sent();
                    form_1 = pdfDoc.getForm();
                    // Log all available form fields
                    console.log('Available form fields:');
                    fields = form_1.getFields();
                    formFieldData_1 = [];
                    fields.forEach(function (field) {
                        var fieldName = field.getName();
                        var fieldType = field.constructor.name;
                        console.log("Field Name: ".concat(fieldName, ", Type: ").concat(fieldType));
                        // Add the field details to the array
                        formFieldData_1.push({
                            fieldName: fieldName,
                            fieldType: fieldType,
                            value: "" // Initially setting value as empty
                        });
                    });
                    jsonData = JSON.stringify(formFieldData_1, null, 2);
                    // Save the JSON data to a file
                    fs.writeFileSync('form-fields.json', jsonData);
                    console.log('Form fields saved to form-fields.json.');
                    // Example of filling out a form field based on its type
                    fields.forEach(function (field) {
                        var fieldName = field.getName();
                        var fieldType = field.constructor.name;
                        if (fieldType === 'PDFTextField') {
                            var textField = form_1.getTextField(fieldName);
                            textField.setText('Sample Text');
                            console.log("Filled text field: ".concat(fieldName));
                        }
                        else if (fieldType === 'PDFCheckBox') {
                            var checkBox = form_1.getCheckBox(fieldName);
                            checkBox.check();
                            console.log("Checked checkbox: ".concat(fieldName));
                        }
                        else {
                            console.log("Unsupported field type: ".concat(fieldType, " for field: ").concat(fieldName));
                        }
                    });
                    // Flatten form and save
                    form_1.flatten();
                    return [4 /*yield*/, pdfDoc.save()];
                case 2:
                    pdfBytes = _a.sent();
                    fs.writeFileSync('filled-form.pdf', pdfBytes);
                    console.log('PDF form filled and saved successfully.');
                    return [3 /*break*/, 4];
                case 3:
                    error_1 = _a.sent();
                    console.error('Error in fillPdfForm:', error_1);
                    if (error_1.message.includes('has no form field')) {
                        console.error('The specified form field was not found. Please check the available fields in the console output above.');
                    }
                    return [3 /*break*/, 4];
                case 4: return [2 /*return*/];
            }
        });
    });
}
fillPdfForm().catch(function (error) {
    console.error('Top-level error:', error);
});
