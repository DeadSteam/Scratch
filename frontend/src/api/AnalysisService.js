/**
 * Analysis Service
 * Single Responsibility: Handle image analysis API calls
 */

import { httpClient } from './HttpClient';

class AnalysisService {
  /**
   * Analyze a single image (incremental).
   * Calculates scratch index for ONE image and appends to scratch_results.
   */
  async analyzeSingleImage(imageId) {
    const response = await httpClient.post(`/analysis/image/${imageId}`);
    return response.data;
  }

  /**
   * Recalculate ALL images in an experiment.
   * Use when ROI changes or a full audit is needed.
   */
  async recalculateExperiment(experimentId) {
    const response = await httpClient.post(
      `/analysis/experiment/${experimentId}/recalculate`,
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

}

export const analysisService = new AnalysisService();

export default AnalysisService;
