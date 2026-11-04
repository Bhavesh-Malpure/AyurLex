import React, { useState } from 'react';
import { apiClient } from '../../services/api-client';

interface ResearchToolsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ResearchToolsModal: React.FC<ResearchToolsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'academic' | 'deadlines' | 'fees' | 'vector'>('academic');

  // Academic Search State
  const [academicQuery, setAcademicQuery] = useState('Curcuma longa clinical trial');
  const [academicLoading, setAcademicLoading] = useState(false);
  const [academicResults, setAcademicResults] = useState<any[]>([]);
  const [academicError, setAcademicError] = useState<string | null>(null);

  // Deadline Calculator State
  const [filingDate, setFilingDate] = useState('2024-03-15');
  const [deadlineResults, setDeadlineResults] = useState<any | null>(null);
  const [deadlineLoading, setDeadlineLoading] = useState(false);

  // Fee Calculator State
  const [applicantType, setApplicantType] = useState('startup');
  const [pagesCount, setPagesCount] = useState(30);
  const [claimsCount, setClaimsCount] = useState(10);
  const [isEFiling, setIsEFiling] = useState(true);
  const [includeEarlyPub, setIncludeEarlyPub] = useState(false);
  const [includeExpedited, setIncludeExpedited] = useState(false);
  const [feeResults, setFeeResults] = useState<any | null>(null);
  const [feeLoading, setFeeLoading] = useState(false);

  // Vector Search State
  const [vectorQuery, setVectorQuery] = useState('Section 3(p) traditional knowledge');
  const [vectorResults, setVectorResults] = useState<any[]>([]);
  const [vectorLoading, setVectorLoading] = useState(false);

  if (!isOpen) return null;

  // Handlers
  const handleAcademicSearch = async () => {
    if (!academicQuery.trim()) return;
    setAcademicLoading(true);
    setAcademicError(null);
    try {
      const res = await apiClient.searchAcademicPapers(academicQuery.trim(), 6);
      setAcademicResults(res.papers || []);
    } catch (err: any) {
      setAcademicError(err.message || 'Failed to search academic repositories');
    } finally {
      setAcademicLoading(false);
    }
  };

  const handleCalculateDeadlines = async () => {
    setDeadlineLoading(true);
    try {
      const res = await apiClient.calculateDeadlines(filingDate);
      setDeadlineResults(res);
    } catch (err: any) {
      alert('Error calculating deadlines: ' + err.message);
    } finally {
      setDeadlineLoading(false);
    }
  };

  const handleCalculateFees = async () => {
    setFeeLoading(true);
    try {
      const res = await apiClient.calculateFees({
        applicantType,
        pagesCount,
        claimsCount,
        isEFiling,
        includeEarlyPub,
        includeExpeditedExam: includeExpedited,
      });
      setFeeResults(res);
    } catch (err: any) {
      alert('Error calculating fees: ' + err.message);
    } finally {
      setFeeLoading(false);
    }
  };

  const handleVectorSearch = async () => {
    if (!vectorQuery.trim()) return;
    setVectorLoading(true);
    try {
      const res = await apiClient.searchVector(vectorQuery.trim());
      setVectorResults(res.chunks || []);
    } catch (err: any) {
      alert('Error in vector retrieval: ' + err.message);
    } finally {
      setVectorLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col border border-gray-200 overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 bg-[#F7FAF8] border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-[#1F2937] flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#0F5132]"></span>
              Ayurlex Advanced Research Workbench & Tools
            </h2>
            <p className="text-xs text-[#6B7280] mt-0.5">
              Statutory calculators, academic evidence retrieval, and hybrid semantic vector tools.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-200 transition-colors"
            title="Close"
          >
            ✕
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 bg-white px-6">
          <button
            onClick={() => setActiveTab('academic')}
            className={`py-3 px-4 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'academic'
                ? 'border-[#0F5132] text-[#0F5132]'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            🎓 Academic & Clinical (PubMed / Crossref)
          </button>
          <button
            onClick={() => setActiveTab('deadlines')}
            className={`py-3 px-4 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'deadlines'
                ? 'border-[#0F5132] text-[#0F5132]'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            ⏱️ Statutory Deadline Calculator
          </button>
          <button
            onClick={() => setActiveTab('fees')}
            className={`py-3 px-4 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'fees'
                ? 'border-[#0F5132] text-[#0F5132]'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            💰 Patent Fee Calculator
          </button>
          <button
            onClick={() => setActiveTab('vector')}
            className={`py-3 px-4 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'vector'
                ? 'border-[#0F5132] text-[#0F5132]'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            🔍 Hybrid Vector Retrieval
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* TAB 1: ACADEMIC SEARCH */}
          {activeTab === 'academic' && (
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={academicQuery}
                  onChange={(e) => setAcademicQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAcademicSearch()}
                  placeholder="Enter botanical compound, formulation, or clinical trial topic..."
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0F5132] text-sm"
                />
                <button
                  onClick={handleAcademicSearch}
                  disabled={academicLoading}
                  className="px-5 py-2.5 bg-[#0F5132] text-white rounded-lg font-medium text-sm hover:bg-[#2E7D5B] transition-colors disabled:opacity-50"
                >
                  {academicLoading ? 'Searching...' : 'Search Papers'}
                </button>
              </div>

              {academicError && (
                <div className="p-3 bg-red-50 text-red-700 text-xs rounded-lg border border-red-200">
                  {academicError}
                </div>
              )}

              <div className="space-y-3">
                {academicResults.length === 0 && !academicLoading && (
                  <p className="text-sm text-gray-500 italic py-4 text-center">
                    Enter a query to retrieve peer-reviewed Ayurvedic & pharmacological research papers.
                  </p>
                )}

                {academicResults.map((paper, idx) => (
                  <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:border-[#2E7D5B] transition-all bg-[#FDFDFD]">
                    <div className="flex items-start justify-between gap-3">
                      <h4 className="font-semibold text-sm text-[#1F2937]">
                        {paper.title}
                      </h4>
                      <span className="px-2 py-0.5 bg-[#E8F5EE] text-[#0F5132] font-semibold text-[11px] rounded uppercase whitespace-nowrap">
                        {paper.source}
                      </span>
                    </div>
                    {paper.authors && (
                      <p className="text-xs text-gray-600 mt-1">
                        <strong>Authors:</strong> {paper.authors}
                      </p>
                    )}
                    {paper.journal && (
                      <p className="text-xs text-gray-500">
                        <strong>Journal / Year:</strong> {paper.journal} ({paper.year || 'N/A'})
                      </p>
                    )}
                    {paper.abstract && (
                      <p className="text-xs text-gray-700 mt-2 line-clamp-3 bg-gray-50 p-2.5 rounded border border-gray-100">
                        {paper.abstract}
                      </p>
                    )}
                    {paper.url && (
                      <div className="mt-2.5">
                        <a
                          href={paper.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-[#0F5132] font-semibold hover:underline flex items-center gap-1"
                        >
                          View Official Source ↗
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: STATUTORY DEADLINES */}
          {activeTab === 'deadlines' && (
            <div className="space-y-4">
              <div className="bg-[#E8F5EE] p-4 rounded-lg border border-[#0F5132]/20 flex items-center justify-between">
                <div>
                  <label className="block text-xs font-semibold text-[#0F5132] uppercase mb-1">
                    Select Application Priority / Provisional Filing Date:
                  </label>
                  <input
                    type="date"
                    value={filingDate}
                    onChange={(e) => setFilingDate(e.target.value)}
                    className="px-3 py-1.5 border border-gray-300 rounded text-sm bg-white font-medium"
                  />
                </div>
                <button
                  onClick={handleCalculateDeadlines}
                  disabled={deadlineLoading}
                  className="px-5 py-2 bg-[#0F5132] text-white rounded-lg font-medium text-sm hover:bg-[#2E7D5B] transition-colors"
                >
                  {deadlineLoading ? 'Calculating...' : 'Compute Statutory Timelines'}
                </button>
              </div>

              {deadlineResults && (
                <div className="space-y-3">
                  <div className="text-xs text-gray-600 font-medium">
                    Priority Date Reference: <strong>{deadlineResults.priority_date}</strong>
                  </div>
                  <div className="overflow-hidden border border-gray-200 rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200 text-left text-xs">
                      <thead className="bg-[#F7FAF8]">
                        <tr>
                          <th className="px-3 py-2.5 font-semibold text-gray-700">Statutory Event</th>
                          <th className="px-3 py-2.5 font-semibold text-gray-700">Statutory Provision</th>
                          <th className="px-3 py-2.5 font-semibold text-gray-700">Due Date</th>
                          <th className="px-3 py-2.5 font-semibold text-gray-700">Description</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 bg-white">
                        {deadlineResults.deadlines.map((item: any, i: number) => (
                          <tr key={i} className="hover:bg-gray-50">
                            <td className="px-3 py-2.5 font-medium text-[#1F2937]">{item.event}</td>
                            <td className="px-3 py-2.5 text-gray-600 font-mono text-[11px]">{item.section_rule}</td>
                            <td className="px-3 py-2.5 font-bold text-[#0F5132]">{item.deadline}</td>
                            <td className="px-3 py-2.5 text-gray-500">{item.description}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: STATUTORY FEES */}
          {activeTab === 'fees' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200 text-xs">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">Applicant Category</label>
                  <select
                    value={applicantType}
                    onChange={(e) => setApplicantType(e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded bg-white"
                  >
                    <option value="natural_person">Natural Person / Individual</option>
                    <option value="startup">DPIIT-Recognized Startup</option>
                    <option value="small_entity">Small Entity (MSME)</option>
                    <option value="large_entity">Others / Large Entity</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">Specification Pages</label>
                  <input
                    type="number"
                    min={1}
                    value={pagesCount}
                    onChange={(e) => setPagesCount(Number(e.target.value))}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded bg-white"
                  />
                  <span className="text-[10px] text-gray-500">First 30 pages free</span>
                </div>
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">Number of Claims</label>
                  <input
                    type="number"
                    min={1}
                    value={claimsCount}
                    onChange={(e) => setClaimsCount(Number(e.target.value))}
                    className="w-full px-2 py-1.5 border border-gray-300 rounded bg-white"
                  />
                  <span className="text-[10px] text-gray-500">First 10 claims free</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-4 text-xs font-medium text-gray-700">
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isEFiling}
                    onChange={(e) => setIsEFiling(e.target.checked)}
                    className="rounded text-[#0F5132]"
                  />
                  Online E-Filing (10% fee reduction)
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeEarlyPub}
                    onChange={(e) => setIncludeEarlyPub(e.target.checked)}
                    className="rounded text-[#0F5132]"
                  />
                  Form 9 (Early Publication)
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeExpedited}
                    onChange={(e) => setIncludeExpedited(e.target.checked)}
                    className="rounded text-[#0F5132]"
                  />
                  Form 18A (Expedited Examination)
                </label>
              </div>

              <button
                onClick={handleCalculateFees}
                disabled={feeLoading}
                className="w-full py-2 bg-[#0F5132] text-white rounded-lg font-medium text-sm hover:bg-[#2E7D5B] transition-colors"
              >
                {feeLoading ? 'Calculating Official Fees...' : 'Compute Official Statutory Fees (INR)'}
              </button>

              {feeResults && (
                <div className="p-4 bg-[#E8F5EE] rounded-lg border border-[#0F5132]/30 space-y-3">
                  <div className="flex items-center justify-between border-b border-[#0F5132]/20 pb-2">
                    <span className="text-sm font-semibold text-gray-800">Total Statutory Fee:</span>
                    <span className="text-xl font-bold text-[#0F5132]">
                      ₹{feeResults.total_official_fee_inr.toLocaleString('en-IN')}
                    </span>
                  </div>
                  <div className="space-y-1.5 text-xs text-gray-700">
                    <p className="font-semibold text-gray-900">Fee Breakdown:</p>
                    {feeResults.fee_breakdown.map((item: any, i: number) => (
                      <div key={i} className="flex justify-between py-0.5 border-b border-gray-200/50">
                        <span>{item.item}</span>
                        <span className="font-mono font-medium">₹{item.amount_inr.toLocaleString('en-IN')}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-[11px] text-gray-500 italic mt-2">
                    Statutory reference: {feeResults.schedule_reference}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: VECTOR RETRIEVAL */}
          {activeTab === 'vector' && (
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={vectorQuery}
                  onChange={(e) => setVectorQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleVectorSearch()}
                  placeholder="Enter legal query for hybrid vector similarity..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0F5132] text-sm"
                />
                <button
                  onClick={handleVectorSearch}
                  disabled={vectorLoading}
                  className="px-5 py-2 bg-[#0F5132] text-white rounded-lg font-medium text-sm hover:bg-[#2E7D5B] transition-colors"
                >
                  {vectorLoading ? 'Searching...' : 'Dense + Sparse Search'}
                </button>
              </div>

              <div className="space-y-3">
                {vectorResults.map((chunk, i) => (
                  <div key={i} className="p-3 border border-gray-200 rounded-lg bg-white hover:border-[#2E7D5B]">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold text-[#0F5132]">{chunk.document_title || 'Statutory Source'}</span>
                      <span className="px-2 py-0.5 bg-gray-100 font-mono text-[10px] rounded text-gray-600">
                        Score: {chunk.hybrid_score || chunk.similarity || 'N/A'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-700 line-clamp-3 bg-gray-50 p-2 rounded">
                      {chunk.chunk_text || chunk.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer with Mandatory Disclaimer */}
        <div className="px-6 py-3 bg-[#F7FAF8] border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
          <span>Ayurlex provides information for research purposes and does not provide legal advice.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 border border-gray-300 rounded text-gray-700 hover:bg-gray-100 font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
