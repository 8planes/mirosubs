class EffectiveSubtitle:
    def __init__(self, subtitle_id, text, start_time, end_time, sub_order):
        self.subtitle_id = subtitle_id
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.sub_order = sub_order

    @classmethod
    def create_for_subtitle(cls, subtitle):
        return EffectiveSubtitle(
            
