import axios, { AxiosInstance } from 'axios';

class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:5000/api') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        console.error('[API Error]', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async getHealth() {
    const response = await this.client.get('/health');
    return response.data;
  }

  async getSystemInfo() {
    const response = await this.client.get('/health/info');
    return response.data;
  }

  // Image operations
  async getImages() {
    const response = await this.client.get('/images');
    return response.data;
  }

  async mountImage(imagePath: string, index: number = 1, readOnly: boolean = false) {
    const response = await this.client.post('/images/mount', {
      imagePath,
      index,
      readOnly,
    });
    return response.data;
  }

  async unmountImage(mountPath: string, commit: boolean = true) {
    const response = await this.client.post('/images/unmount', {
      mountPath,
      commit,
    });
    return response.data;
  }

  async getImageInfo(imagePath: string) {
    const response = await this.client.get(`/images/info`, {
      params: { imagePath },
    });
    return response.data;
  }

  // Component operations
  async getComponents(mountPath: string) {
    const response = await this.client.get(`/components`, {
      params: { mountPath },
    });
    return response.data;
  }

  async removeComponent(mountPath: string, componentName: string) {
    const response = await this.client.post('/components/remove', {
      mountPath,
      componentName,
    });
    return response.data;
  }

  // Workflow operations
  async getWorkflows() {
    const response = await this.client.get('/workflows');
    return response.data;
  }

  async executeWorkflow(workflowId: string, parameters: Record<string, any>) {
    const response = await this.client.post(`/workflows/${workflowId}/execute`, parameters);
    return response.data;
  }

  async getWorkflowStatus(executionId: string) {
    const response = await this.client.get(`/workflows/executions/${executionId}`);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
