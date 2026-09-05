import React, { useState } from 'react';
import { Form, FormQuestion, QuestionType, FormType } from '../../types';
import { api } from '../../services/api';
import { 
  Plus, 
  Trash2, 
  ArrowUp, 
  ArrowDown, 
  Eye, 
  Send, 
  CheckCircle, 
  FileText, 
  ListChecks, 
  CheckSquare, 
  Calendar, 
  Star, 
  Hash, 
  AlignLeft, 
  ChevronRight,
  Sparkles,
  Users
} from 'lucide-react';

interface OrgFormBuilderProps {
  forms: Form[];
  programmeId: string;
  onRefresh: () => void;
}

export const OrgFormBuilder: React.FC<OrgFormBuilderProps> = ({ forms, programmeId, onRefresh }) => {
  const [selectedForm, setSelectedForm] = useState<Form | null>(forms[0] || null);
  const [isEditing, setIsEditing] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [viewResponsesModal, setViewResponsesModal] = useState<any[] | null>(null);

  // Form Editor State
  const [formTitle, setFormTitle] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formType, setFormType] = useState<FormType>('BASELINE');
  const [questions, setQuestions] = useState<Partial<FormQuestion>[]>([]);

  const startNewForm = () => {
    setFormTitle('New Custom Participant Survey');
    setFormDesc('Please answer each question carefully to assist our programme monitoring.');
    setFormType('MONITORING');
    setQuestions([
      {
        id: `q_new_1`,
        question_text: 'How is the training pace and session comprehension going?',
        question_type: 'RATING_SCALE',
        required: true,
        options: ['1 - Needs Improvement', '2', '3', '4', '5 - Excellent'],
        order: 1
      },
      {
        id: `q_new_2`,
        question_text: 'Are you facing any attendance or commute challenges?',
        question_type: 'YES_NO',
        required: true,
        options: ['Yes', 'No'],
        order: 2
      },
      {
        id: `q_new_3`,
        question_text: 'Please describe any support you require from the field response team.',
        question_type: 'LONG_TEXT',
        required: false,
        options: [],
        order: 3
      }
    ]);
    setSelectedForm(null);
    setIsEditing(true);
  };

  const addQuestion = () => {
    const newQ: Partial<FormQuestion> = {
      id: `q_${Date.now()}`,
      question_text: 'New Question',
      question_type: 'SHORT_TEXT',
      required: true,
      options: ['Option 1', 'Option 2'],
      order: questions.length + 1
    };
    setQuestions([...questions, newQ]);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const moveQuestion = (index: number, direction: 'up' | 'down') => {
    if (direction === 'up' && index === 0) return;
    if (direction === 'down' && index === questions.length - 1) return;
    const targetIdx = direction === 'up' ? index - 1 : index + 1;
    const newArr = [...questions];
    const temp = newArr[index];
    newArr[index] = newArr[targetIdx];
    newArr[targetIdx] = temp;
    setQuestions(newArr);
  };

  const updateQuestionField = (index: number, field: string, value: any) => {
    const updated = [...questions];
    (updated[index] as any)[field] = value;
    setQuestions(updated);
  };

  const saveForm = async (publishImmediately: boolean = false) => {
    if (!formTitle.trim()) return alert('Please provide a form title');
    const payload = {
      title: formTitle,
      description: formDesc,
      form_type: formType,
      status: publishImmediately ? 'PUBLISHED' : 'DRAFT',
      questions
    };

    if (selectedForm && selectedForm.id) {
      await api.updateForm(selectedForm.id, payload);
    } else {
      await api.createForm(programmeId, payload);
    }
    setIsEditing(false);
    onRefresh();
  };

  const publishExisting = async (formId: string) => {
    await api.publishForm(formId);
    onRefresh();
  };

  const loadResponses = async (form: Form) => {
    const resps = await api.getFormResponses(form.id);
    setViewResponsesModal(resps);
  };

  const openFormForEdit = (f: Form) => {
    setSelectedForm(f);
    setFormTitle(f.title);
    setFormDesc(f.description || '');
    setFormType(f.form_type);
    setQuestions(f.questions || []);
    setIsEditing(true);
  };

  const questionTypeLabels: Record<QuestionType, string> = {
    SHORT_TEXT: 'Short Text',
    LONG_TEXT: 'Paragraph / Long Text',
    NUMBER: 'Number',
    MULTIPLE_CHOICE: 'Multiple Choice (Single)',
    CHECKBOX: 'Checkboxes (Multi-select)',
    DROPDOWN: 'Dropdown Menu',
    YES_NO: 'Yes / No',
    RATING_SCALE: 'Rating Scale (1-5 / 1-10)',
    DATE: 'Date',
    FILE_UPLOAD: 'File Upload'
  };

  return (
    <div className="space-y-6" id="form-builder-view">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Custom Forms & Survey Engine</h2>
          <p className="text-xs text-slate-500 mt-1">
            Dynamic survey builder connected directly to programme cohorts & outcome measurement.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={startNewForm}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 shadow-sm cursor-pointer"
            id="btn-create-custom-form"
          >
            <Plus className="w-4 h-4" />
            Create New Form
          </button>
        </div>
      </div>

      {/* Main Grid: Form List & Active Form / Editor */}
      {!isEditing ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {forms.map((f) => {
            const isSelected = selectedForm?.id === f.id;
            return (
              <div
                key={f.id}
                onClick={() => setSelectedForm(f)}
                className={`bg-white rounded-xl border p-5 transition-all cursor-pointer flex flex-col justify-between shadow-sm ${
                  isSelected ? 'border-indigo-600 ring-2 ring-indigo-100' : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-md uppercase tracking-wider ${
                      f.form_type === 'BASELINE' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' :
                      f.form_type === 'MONITORING' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                      f.form_type === 'ENDLINE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      'bg-slate-100 text-slate-700 border border-slate-200'
                    }`}>
                      {f.form_type}
                    </span>
                    <span className={`text-[11px] font-medium ${f.status === 'PUBLISHED' ? 'text-emerald-600' : 'text-slate-400'}`}>
                      {f.status}
                    </span>
                  </div>

                  <h3 className="font-bold text-slate-900 text-sm leading-snug line-clamp-2">{f.title}</h3>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">{f.description}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
                  <div className="flex items-center gap-1">
                    <Users className="w-3.5 h-3.5 text-slate-400" />
                    <span className="font-semibold text-slate-800">{f.responses_count || 0}</span> Responses
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={(e) => { e.stopPropagation(); openFormForEdit(f); }}
                      className="text-slate-600 hover:text-slate-900 font-medium text-xs px-2 py-1 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); loadResponses(f); }}
                      className="text-indigo-600 hover:text-indigo-700 font-medium text-xs px-2 py-1 bg-indigo-50 rounded-md hover:bg-indigo-100 transition-colors"
                    >
                      View
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Form Editor Mode (Google Forms Style) */
        <div className="space-y-4">
          {/* Header & Meta Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-indigo-600" />
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-semibold text-indigo-600 tracking-wider uppercase">
                Custom Form Designer
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPreviewMode(!previewMode)}
                  className="px-3 py-1.5 rounded-md border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <Eye className="w-3.5 h-3.5" />
                  {previewMode ? 'Back to Editor' : 'Live Preview'}
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-3 py-1.5 rounded-md text-xs font-medium text-slate-500 hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Form Title</label>
                <input
                  type="text"
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  placeholder="Form Title (e.g. Bi-Weekly Participant Check-In)"
                  className="w-full text-lg font-bold text-slate-900 border-b border-slate-200 pb-1 focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description & Instructions</label>
                <textarea
                  rows={2}
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                  placeholder="Explain the purpose of this survey to participants..."
                  className="w-full text-xs text-slate-600 border border-slate-200 rounded-lg p-2.5 focus:border-indigo-600 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Form Lifecycle Type</label>
                  <select
                    value={formType}
                    onChange={(e) => setFormType(e.target.value as FormType)}
                    className="w-full text-xs border border-slate-200 rounded-lg p-2 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="BASELINE">Baseline Form (Before Programme)</option>
                    <option value="MONITORING">Monitoring Form (During Programme)</option>
                    <option value="ENDLINE">Endline Form (Immediately After)</option>
                    <option value="FOLLOW_UP">Follow-up Form (Longitudinal 3/6/12 Months)</option>
                    <option value="CUSTOM">Custom Ad-Hoc Survey</option>
                  </select>
                </div>

                <div className="flex items-end gap-2">
                  <button
                    onClick={() => saveForm(false)}
                    className="flex-1 py-2 rounded-md border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer shadow-xs"
                  >
                    Save Draft
                  </button>
                  <button
                    onClick={() => saveForm(true)}
                    className="flex-1 py-2 rounded-md bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium transition-colors flex items-center justify-center gap-1 shadow-sm cursor-pointer"
                  >
                    <Send className="w-3.5 h-3.5" />
                    Publish to Cohort
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Question List (Editor vs Live Preview) */}
          {!previewMode ? (
            <div className="space-y-3">
              {questions.map((q, idx) => (
                <div key={q.id || idx} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-colors">
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-600 font-semibold text-xs flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <span className="text-xs font-medium text-slate-500">Question {idx + 1}</span>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => moveQuestion(idx, 'up')}
                        disabled={idx === 0}
                        className="p-1 text-slate-400 hover:text-slate-700 disabled:opacity-30 cursor-pointer"
                        title="Move Up"
                      >
                        <ArrowUp className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => moveQuestion(idx, 'down')}
                        disabled={idx === questions.length - 1}
                        className="p-1 text-slate-400 hover:text-slate-700 disabled:opacity-30 cursor-pointer"
                        title="Move Down"
                      >
                        <ArrowDown className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => removeQuestion(idx)}
                        className="p-1 text-rose-500 hover:text-rose-700 ml-1 cursor-pointer"
                        title="Delete Question"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                    <div className="md:col-span-2">
                      <input
                        type="text"
                        value={q.question_text || ''}
                        onChange={(e) => updateQuestionField(idx, 'question_text', e.target.value)}
                        placeholder="Enter question text..."
                        className="w-full text-xs font-medium border border-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <select
                        value={q.question_type || 'SHORT_TEXT'}
                        onChange={(e) => updateQuestionField(idx, 'question_type', e.target.value)}
                        className="w-full text-xs border border-slate-200 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none font-medium"
                      >
                        {Object.entries(questionTypeLabels).map(([val, label]) => (
                          <option key={val} value={val}>{label}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Options Manager for Multi-Choice / Checkbox / Dropdown */}
                  {['MULTIPLE_CHOICE', 'CHECKBOX', 'DROPDOWN', 'RATING_SCALE'].includes(q.question_type || '') && (
                    <div className="mt-2 pl-4 border-l-2 border-indigo-200 space-y-1.5">
                      <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Choices / Options:</div>
                      {(q.options || []).map((opt, optIdx) => (
                        <div key={optIdx} className="flex items-center gap-2">
                          <span className="w-3.5 h-3.5 rounded-full border border-slate-300 bg-slate-50 shrink-0" />
                          <input
                            type="text"
                            value={opt}
                            onChange={(e) => {
                              const newOpts = [...(q.options || [])];
                              newOpts[optIdx] = e.target.value;
                              updateQuestionField(idx, 'options', newOpts);
                            }}
                            className="text-xs px-2 py-1 border border-slate-200 rounded flex-1 focus:border-indigo-500 focus:outline-none"
                          />
                          <button
                            onClick={() => {
                              const newOpts = (q.options || []).filter((_, i) => i !== optIdx);
                              updateQuestionField(idx, 'options', newOpts);
                            }}
                            className="text-slate-400 hover:text-rose-500 text-xs px-1 cursor-pointer"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                      <button
                        onClick={() => {
                          const newOpts = [...(q.options || []), `Option ${(q.options?.length || 0) + 1}`];
                          updateQuestionField(idx, 'options', newOpts);
                        }}
                        className="text-xs font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1 pt-1 cursor-pointer"
                      >
                        <Plus className="w-3 h-3" /> Add Choice
                      </button>
                    </div>
                  )}

                  <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={q.required !== false}
                        onChange={(e) => updateQuestionField(idx, 'required', e.target.checked)}
                        className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5"
                      />
                      <span>Required question</span>
                    </label>
                    <span className="text-[11px] text-slate-400">Order: {idx + 1}</span>
                  </div>
                </div>
              ))}

              <button
                onClick={addQuestion}
                className="w-full py-3.5 border-2 border-dashed border-slate-200 hover:border-indigo-400 rounded-xl text-xs font-medium text-slate-600 hover:text-indigo-600 transition-colors flex items-center justify-center gap-2 bg-white cursor-pointer shadow-sm"
                id="btn-add-question"
              >
                <Plus className="w-4 h-4" /> Add Question to Form
              </button>
            </div>
          ) : (
            /* Live Form Preview */
            <div className="bg-white rounded-xl border border-slate-200 p-8 max-w-2xl mx-auto shadow-sm space-y-6">
              <div>
                <h2 className="text-xl font-bold text-slate-900">{formTitle}</h2>
                <p className="text-xs text-slate-600 mt-1">{formDesc}</p>
                <span className="inline-block mt-2 px-2.5 py-0.5 rounded text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
                  Preview Mode
                </span>
              </div>

              <div className="space-y-5 divide-y divide-slate-100">
                {questions.map((q, idx) => (
                  <div key={idx} className="pt-4 first:pt-0 space-y-2">
                    <div className="text-xs font-semibold text-slate-800 flex items-start gap-1">
                      <span>{idx + 1}. {q.question_text}</span>
                      {q.required && <span className="text-rose-500">*</span>}
                    </div>

                    {q.question_type === 'SHORT_TEXT' && (
                      <input type="text" disabled placeholder="Short answer text" className="w-full text-xs p-2 border border-slate-200 rounded bg-slate-50" />
                    )}

                    {q.question_type === 'LONG_TEXT' && (
                      <textarea disabled rows={3} placeholder="Detailed paragraph response..." className="w-full text-xs p-2 border border-slate-200 rounded bg-slate-50" />
                    )}

                    {q.question_type === 'YES_NO' && (
                      <div className="flex items-center gap-4 text-xs">
                        <label className="flex items-center gap-1.5"><input type="radio" disabled /> Yes</label>
                        <label className="flex items-center gap-1.5"><input type="radio" disabled /> No</label>
                      </div>
                    )}

                    {['MULTIPLE_CHOICE', 'CHECKBOX', 'DROPDOWN', 'RATING_SCALE'].includes(q.question_type || '') && (
                      <div className="space-y-1 text-xs">
                        {(q.options || []).map((opt, oIdx) => (
                          <div key={oIdx} className="flex items-center gap-2">
                            <input type={q.question_type === 'CHECKBOX' ? 'checkbox' : 'radio'} disabled />
                            <span>{opt}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* View Submitted Responses Modal */}
      {viewResponsesModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-3xl w-full p-6 shadow-xl border border-slate-200 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Submitted Participant Responses</h3>
                <p className="text-xs text-slate-500">Viewing real responses recorded by programme beneficiaries.</p>
              </div>
              <button onClick={() => setViewResponsesModal(null)} className="text-slate-400 hover:text-slate-600 font-bold p-1 cursor-pointer">✕</button>
            </div>

            {viewResponsesModal.length === 0 ? (
              <div className="text-center py-10 text-xs text-slate-500">No responses recorded yet for this form.</div>
            ) : (
              <div className="space-y-4">
                {viewResponsesModal.map((resp, i) => (
                  <div key={resp.id || i} className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                    <div className="flex items-center justify-between font-bold text-slate-900 pb-2 border-b border-slate-200">
                      <span>{resp.beneficiary_name || 'Participant'}</span>
                      <span className="text-[11px] font-normal text-slate-500">{new Date(resp.submitted_at || Date.now()).toLocaleDateString()}</span>
                    </div>

                    <div className="mt-3 space-y-2">
                      {Object.entries(resp.answers || {}).map(([qKey, aVal]) => (
                        <div key={qKey} className="bg-white p-2.5 rounded border border-slate-100">
                          <span className="font-semibold text-slate-700 block mb-0.5">{qKey}:</span>
                          <span className="text-slate-900 font-medium">
                            {Array.isArray(aVal) ? aVal.join(', ') : String(aVal)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
