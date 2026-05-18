import { BaseApiService } from './BaseApiService';

class AdviceService extends BaseApiService {
  constructor() { super('/advices', 100); }
}

export const adviceService = new AdviceService();
export default AdviceService;
