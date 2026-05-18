import { BaseApiService } from './BaseApiService';

class FilmService extends BaseApiService {
  constructor() {
    super('/films', 100);
  }
}

export const filmService = new FilmService();
export default FilmService;
