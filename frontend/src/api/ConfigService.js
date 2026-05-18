import { BaseApiService } from './BaseApiService';

class ConfigService extends BaseApiService {
  constructor() {
    super('/equipment-configs', 100);
  }
}

export const configService = new ConfigService();
export default ConfigService;
