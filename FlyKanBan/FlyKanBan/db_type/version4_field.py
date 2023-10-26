from FlyKanBan.db_type.custom_field import CustomField
from FlyKanBan.db_type.custom_field import CustomValue


class Version4(CustomValue):
	generations:int = 0
	milestones:int = -1
	stories:int = -1
	bugs:int = -1

	def __init__(self, value:str|None):
		if value is None:
			return
		value = str(value)
		vers = value.split('.')
		vers_cnt = len(vers)
		if vers_cnt >= 1:
			self.generations = int(vers[0])
		if vers_cnt >= 2:
			self.milestones = int(vers[1])
		if vers_cnt >= 3:
			self.stories = int(vers[2])
		if vers_cnt >= 4:
			self.bugs = int(vers[3])

	def db_value(self)->str:
		ver_str = f'{self.generations}' 
		if self.milestones >= 0:
			ver_str += f'.{self.milestones}'
			if self.stories >= 0:
				ver_str += f'.{self.stories}'
				if self.bugs >= 0:
					ver_str += f'.{self.bugs}'
		return ver_str

	def __eq__(self, __value: object) -> bool:
		if __value is None:
			return self.generations == 0 \
				and self.milestones == -1
		
		if isinstance(__value, int):
			return self.generations == __value
		
		if isinstance(__value, str):
			__value = Version4(__value)

		if isinstance(__value, Version4):
			return self.generations == __value.generations \
				and self.milestones == __value.milestones \
				and self.stories == __value.stories \
				and self.bugs == __value.bugs
		
		return False


class FVer(CustomField):
	data_type = Version4

	def __init__(self, *args, **kwargs):
		kwargs['default'] = '0'
		super().__init__(*args, **kwargs)		