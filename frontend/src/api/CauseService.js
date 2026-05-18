import { BaseApiService } from './BaseApiService';

class CauseService extends BaseApiService {
  constructor() { super('/causes', 100); }
}

export const causeService = new CauseService();
export default CauseService;
