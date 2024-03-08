class SuccessTracker:
    def __init__(self, success_threshhold):
        self.success_threshhold = success_threshhold
        self.path_count = 0
        self.current_path = []
        self.previous_path = []

    def start_new_path(self):
        self.current_path = []

    def update_path(self, state):
        path_step = (state.x, state.y, state.key_found)
        self.current_path.append(path_step)

    def save_path(self, current_path):
        self.previous_path = current_path
        #self.path_count += 1

    def reset_success(self):
        self.path_count = 0


    def track_success(self, current_path):
        #path_key = tuple(self.current_path)
        if self.path_count <= self.success_threshhold and current_path == self.previous_path:
            return True
        elif self.path_count >= 0 and current_path != self.previous_path:
            return False
