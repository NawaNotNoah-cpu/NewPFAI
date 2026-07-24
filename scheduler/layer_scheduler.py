class LayerScheduler:

    def __init__(self, intervals=10):

        self.intervals = intervals
        self.targets = []
        self.index = 0


    def initialize(self, total_layers):

        if total_layers is None:
            raise ValueError(
                "Total layer count unavailable"
            )

        step = total_layers / self.intervals

        self.targets = [
            round(step * i)
            for i in range(1, self.intervals + 1)
        ]

        self.index = 0

        print(
            "Inspection layers:",
            self.targets
        )


    def should_capture(self, current_layer):

        if self.index >= len(self.targets):
            return False


        target = self.targets[self.index]


        if current_layer >= target:

            self.index += 1

            return True


        return False


    def next_target(self):

        if self.index < len(self.targets):
            return self.targets[self.index]

        return None