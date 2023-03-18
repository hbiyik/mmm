// SPDX-License-Identifier: GPL-2.0
/*
 *  linux/drivers/char/mem.c
 *
 *  Copyright (C) 1991, 1992  Linus Torvalds
 *
 *  Boogie: Adapted to bypass security checks and only focus physical memory
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/miscdevice.h>
#include <linux/uaccess.h>
#include <linux/io.h>

static int uncached_access(struct file *file, phys_addr_t addr){
	if (file->f_flags & O_DSYNC)
		return 1;
	return addr >= __pa(high_memory);
}


pgprot_t phys_mem_access_prot(struct file *file, unsigned long pfn, unsigned long size, pgprot_t vma_prot){

	phys_addr_t offset = pfn << PAGE_SHIFT;

	if (uncached_access(file, offset))
		return pgprot_noncached(vma_prot);
	return vma_prot;
}


static const struct vm_operations_struct mmap_mem_ops = {
};

static int insec_mem_proc_open(struct inode *inode, struct file *filp){
	return 0;
}

static ssize_t insec_mem_proc_write(struct file *filp, const char __user *buffer, size_t count, loff_t *ppos){
	long phys_offset = *ppos;
	void *virt = __va(phys_offset);
	
	if (virt == NULL)
		return -EFAULT;
    //(void)! is only to surpress useless warning messages that are interpreted as error
	(void)!copy_from_user(virt, buffer, count);
	*ppos += count;
	return count;
}

static inline bool should_stop_iteration(void){
	if (need_resched())
		cond_resched();
	return fatal_signal_pending(current);
}

static inline unsigned long size_inside_page(unsigned long start, unsigned long size){
	unsigned long sz;

	sz = PAGE_SIZE - (start & (PAGE_SIZE - 1));

	return min(sz, size);
}

static ssize_t insec_mem_proc_read(struct file *filp, char __user *buffer, size_t count, loff_t *ppos){
	phys_addr_t p = *ppos;
	ssize_t read, sz;
	void *ptr;
	char *bounce;
	int err;

	if (p != *ppos)
		return 0;

	read = 0;

	bounce = kmalloc(PAGE_SIZE, GFP_KERNEL);
	if (!bounce)
		return -ENOMEM;

	while (count > 0) {
		unsigned long remaining;

		sz = size_inside_page(p, count);

		err = -EFAULT;

		ptr = __va(p);
		if (!ptr)
			goto failed;

		err = copy_from_kernel_nofault(bounce, ptr, sz);
		if (err)
			goto failed;

		err = -EFAULT;

		remaining = copy_to_user(buffer, bounce, sz);

		if (remaining)
			goto failed;

		buffer += sz;
		p += sz;
		count -= sz;
		read += sz;
		if (should_stop_iteration())
			break;
	}
	kfree(bounce);

	*ppos += read;
	return read;

failed:
	kfree(bounce);
	return err;
}

static loff_t insec_mem_lseek(struct file *file, loff_t offset, int orig){
	loff_t ret;
	inode_lock(file_inode(file));
	switch (orig) {
	case SEEK_CUR:
		offset += file->f_pos;
		file->f_pos = offset;
		ret = offset;
		break;
	case SEEK_SET:
		file->f_pos = offset;
		ret = file->f_pos;
		break;
	default:
		ret = -EINVAL;
	}
	inode_unlock(file_inode(file));
	return ret;
}

static int insec_mem_mmap(struct file *file, struct vm_area_struct *vma){
	size_t size = vma->vm_end - vma->vm_start;
	vma->vm_page_prot = phys_mem_access_prot(file, vma->vm_pgoff,
						 size,
						 vma->vm_page_prot);

	vma->vm_ops = &mmap_mem_ops;

	/* Remap-pfn-range will mark the range VM_IO */
	if (remap_pfn_range(vma,
			    vma->vm_start,
			    vma->vm_pgoff,
			    size,
			    vma->vm_page_prot)) {
		return -EAGAIN;
	}
	return 0;
}

static const struct file_operations insec_mem_fops = {
	.owner = THIS_MODULE,
	.open = insec_mem_proc_open,
	.read = insec_mem_proc_read,
	.write = insec_mem_proc_write,
	.llseek = insec_mem_lseek,
	.mmap = insec_mem_mmap,
};

struct miscdevice insec_mem_dev = {
    .minor = 1,
    .name = "insecure_mem",
    .fops = &insec_mem_fops,
};

static int __init insec_mem_init(void){
	int error;

	error = misc_register(&insec_mem_dev);
    if (error) {
        return error;
    }
	return 0;
}

static void __exit insec_mem_cleanup(void){
    misc_deregister(&insec_mem_dev);
}

module_init(insec_mem_init);
module_exit(insec_mem_cleanup);
MODULE_LICENSE("GPL");
