/**
 * Analysis Service
 * Single Responsibility: Handle image analysis API calls
 */

import { httpClient } from './HttpClient';

class AnalysisService {
  /**
   * Analyze scratch resistance
   */
  async analyzeScratchResistance(analysisRequest, saveToExperiment = true) {
    const response = await httpClient.post(
      `/analysis/scratch-resistance?save_to_experiment=${saveToExperiment}`,
      analysisRequest,
    );
    return response.data;
  }

  /**
   * Get image histogram
   */
  async getImageHistogram(imageId) {
    const response = await httpClient.get(`/analysis/histogram/${imageId}`);
    return response.data;
  }

  /**
   * Quick analysis of all experiment images
   */
  async quickExperimentAnalysis(experimentId, params = {}) {
    const { skip = 0, limit = 100 } = params;
    const response = await httpClient.get(
      `/analysis/experiment/${experimentId}/quick-analysis`,
      { skip, limit },
    );
    return response.data;
  }
}

export const analysisService = new AnalysisService();

export default AnalysisService;



