
export type ItemStatus = 'review' | 'kept';

export interface CapturedItem {
  id: string;
  blob: Blob;
  url: string;
  latitude?: number;
  longitude?: number;
  status: ItemStatus;
}
