/**
 * In-memory cache of blob object URLs for authenticated images.
 * Kept separate from HttpClient/ImageService to avoid circular imports.
 */

/** @type {Map<string, string>} */
const blobUrls = new Map();

export function getCachedBlobUrl(imageId) {
  return blobUrls.get(imageId) ?? null;
}

export function setCachedBlobUrl(imageId, objectUrl) {
  blobUrls.set(imageId, objectUrl);
}

export function revokeBlobUrl(imageId) {
  const url = blobUrls.get(imageId);
  if (url) {
    URL.revokeObjectURL(url);
    blobUrls.delete(imageId);
  }
}

export function revokeAllBlobUrls() {
  blobUrls.forEach((url) => URL.revokeObjectURL(url));
  blobUrls.clear();
}
