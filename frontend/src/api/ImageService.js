/**
 * Image Service
 * Single Responsibility: Handle image API calls
 */

import { httpClient } from './HttpClient';

class ImageService {
  /**
   * Get images by experiment ID
   */
  async getByExperimentId(experimentId, params = {}) {
    const { skip = 0, limit = 100 } = params;
    const response = await httpClient.get(`/images/experiment/${experimentId}`, { skip, limit });
    return response;
  }

  /**
   * Get image by ID
   */
  async getById(id) {
    const response = await httpClient.get(`/images/${id}`);
    return response.data;
  }

  /**
   * Upload image (multipart form)
   */
  async upload(file, experimentId, passes = 0) {
    const formData = new FormData();
    formData.append('file', file);
    
    const url = `/images/upload?experiment_id=${experimentId}&passes=${passes}`;
    const response = await httpClient.postFormData(url, formData);
    return response.data;
  }

  /**
   * Delete image
   */
  async delete(id) {
    const response = await httpClient.delete(`/images/${id}`);
    return response;
  }

  /**
   * Delete all images for experiment
   */
  async deleteAllByExperiment(experimentId) {
    const response = await httpClient.delete(`/images/experiment/${experimentId}/all`);
    return response;
  }

}

export const imageService = new ImageService();

export default ImageService;



