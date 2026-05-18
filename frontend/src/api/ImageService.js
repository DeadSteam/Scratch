/**
 * Image Service
 * Single Responsibility: Handle image API calls
 */

import { httpClient } from './HttpClient';
import {
  getCachedBlobUrl,
  revokeAllBlobUrls as clearBlobCache,
  revokeBlobUrl,
  setCachedBlobUrl,
} from './imageBlobCache';

class ImageService {
  /**
   * Get images by experiment ID
   */
  async getByExperimentId(experimentId, params = {}) {
    const { skip = 0, limit = 100 } = params;
    const response = await httpClient.get(`/images/experiment/${experimentId}`, {
      skip,
      limit,
    });
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
    revokeBlobUrl(id);
    return response;
  }

  /**
   * Load image binary with Bearer auth and return a blob object URL for &lt;img src&gt;.
   */
  async getAuthenticatedImageUrl(imageId) {
    if (!imageId) return null;

    const cached = getCachedBlobUrl(imageId);
    if (cached) return cached;

    const blob = await httpClient.getBlob(`/images/${imageId}/data`);
    const objectUrl = URL.createObjectURL(blob);
    setCachedBlobUrl(imageId, objectUrl);
    return objectUrl;
  }

  revokeAuthenticatedImageUrl(imageId) {
    revokeBlobUrl(imageId);
  }

  revokeAllBlobUrls() {
    clearBlobCache();
  }

  /**
   * Delete all images for experiment
   */
  async deleteAllByExperiment(experimentId) {
    const response = await httpClient.delete(
      `/images/experiment/${experimentId}/all`,
    );
    clearBlobCache();
    return response;
  }
}

export const imageService = new ImageService();

export default ImageService;
