# This file provides a wrapper on memory access, similarly to working with
# pointers in low level languages
# The memory is organized in blocks of a single byte


# use C compatible data types for maximum memory efficiency
import ctypes

class MemoryRequest:
    def __init__(self, agent_id: int, round_id: int, operation_type: str, content: str = None):
        self.agent_id = agent_id
        self.round_id = round_id
        self.content = content
        self.operation_type = operation_type

class Memory:
    def __init__(self, size=1024):
        self.size = size
        """ makes an array of bytes, typically how memory is organized """
        self.memory = (ctypes.c_ubyte * size)()  # C unsigned char
        self.free_blocks = [(0, size - 1)]       # 空闲块记录数组，初始化时只有一个完整的空闲块，每一个元组都记录对应空闲块的起始下标和结束下标

    # malloc(3) implementation
    def mem_alloc(self, size):
        for i, (start, end) in enumerate(self.free_blocks): # 遍历空闲内存块数组，检查每一个内存块的起始下标和结束下标
            block_size = end - start + 1             # 计算空闲块的大小
            if block_size >= size:                   # 如果空闲块的大小大于等于申请内存的大小，则将该内存块分配出来
                allocated_start = start
                allocated_end = start + size - 1
                if allocated_end == end:             # 如果空闲块的大小恰好等于要分配的大小，直接从空闲块中删除空闲记录
                    self.free_blocks.pop(i)
                else:                                # 否则，将多余的内存拆出来，记录一个新的空闲块记录
                    self.free_blocks[i] = (allocated_end + 1, end)
                return allocated_start               # 返回空闲块的起始下标
        raise MemoryError("No sufficient memory available.")  # 找不到合适的内存，抛出异常

    def mem_clear(self, start, size):
        allocated_end = start + size - 1
        self.free_blocks.append((start, allocated_end))  # 在空闲数组中添加空闲块，这里没有做块的合并，可能会产生大量碎片 --- note
        self.free_blocks.sort()                          # 空闲块记录排序，按照起始下标

    # memcpy(3) implementation
    def mem_write(self, address, data):
        size = len(data)
        if address + size > self.size:                   # 检查是否超出内存块范围
            raise MemoryError("Not enough space to write data.")
        for i in range(size):
            self.memory[address + i] = data[i]           # 逐个写入

    # similar to dereferencing pointers
    def mem_read(self, address, size):
        data = self.memory[address:address + size]       # 直接取出数组切片
        return data

# abstract implementation of memory utilities for thread safe access
class BaseMemoryManager:
    def __init__(self, max_memory_block_size, memory_block_num):
        pass

    def run(self):
        pass

    def start(self):
        """start the scheduler"""
        self.active = True
        self.thread.start()

    def stop(self):
        """stop the scheduler"""
        self.active = False
        self.thread.join()

    def mem_write(self, content: str):
        pass

    def mem_read(self, agent_id):
        pass

    def mem_alloc(self, agent_id):
        pass

    def mem_clear(self):
        pass
