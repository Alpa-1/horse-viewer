export interface Todo {
  id: number;
  content: string;
}

export interface Meta {
  totalCount: number;
}

export interface Horse {
  id: number;
  bitmap: ImageBitmap;
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  opacity: number;
  url: string;
  color: string;
  title: string;
}
