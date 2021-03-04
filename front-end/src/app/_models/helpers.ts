import {environment} from '../../environments/environment';

export function validFileSize(file: File): boolean {
  return sizeInMB(file.size) <= environment.maxFileSize;
}

function sizeInMB(sizeInBytes): number{
  return sizeInBytes / 1024 / 1024;
}

