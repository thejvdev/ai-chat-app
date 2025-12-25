export type ApiUser = {
  id: string;
  full_name: string;
  email: string;
};

export type ApiError = {
  status: number;
  data: { detail?: string };
};

export function isApiError(err: unknown): err is ApiError {
  return (
    typeof err === "object" && err !== null && "status" in err && "data" in err
  );
}
