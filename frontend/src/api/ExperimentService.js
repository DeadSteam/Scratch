import { BaseApiService } from './BaseApiService';

class ExperimentService extends BaseApiService {
  constructor() {
    super('/experiments', 50);
  }

  async getByUserId(userId, params = {}) {
    const { skip = 0, limit = this.defaultLimit } = params;
    return this.http.get(`${this.basePath}/user/${userId}`, { skip, limit });
  }

  async getWithImages(id) {
    const response = await this.http.get(`${this.basePath}/${id}/with-images`);
    return response.data;
  }

  async downloadReport(id) {
    return this.http.getBlob(`${this.basePath}/${id}/report`);
  }
}

export const experimentService = new ExperimentService();
export default ExperimentService;
