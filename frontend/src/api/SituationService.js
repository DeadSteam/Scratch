import { BaseApiService } from './BaseApiService';

class SituationService extends BaseApiService {
  constructor() { super('/situations', 100); }
}

export const situationService = new SituationService();
export default SituationService;
