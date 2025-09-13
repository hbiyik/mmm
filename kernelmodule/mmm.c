// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * mmm.c
 *
 * Copyright 2025 boogie
 */

#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/regulator/consumer.h>


struct arg_info {
	char name[32];
	int value;
};

struct arg_set {
	struct arg_info info;
	int min;
	int max;
};


#define IOCTL_MAGIC	('m')
#define CMD_GET_REGULATOR _IOWR(IOCTL_MAGIC, 0, struct arg_info)
#define CMD_SET_REGULATOR _IOWR(IOCTL_MAGIC, 1, struct arg_set)


static long mmm_ioctl(struct file *file, unsigned int cmd, unsigned long arg){
	struct miscdevice* mdev = file->private_data;
	struct regulator* reg = NULL;
	void __user * argp = (void __user *)arg;
	int ret = 0;

	if(cmd == CMD_GET_REGULATOR){
		struct arg_info arginfo;

		if (copy_from_user(&arginfo, argp, sizeof(struct arg_info)))
			return -EFAULT;

		reg = devm_regulator_get(mdev->this_device, arginfo.name);
		if(IS_ERR(reg))
			return PTR_ERR(reg);

		ret = regulator_get_voltage(reg);
		if (ret < 0)
			goto error;

		arginfo.value = ret;

		if (copy_to_user(argp, &arginfo, sizeof(struct arg_info)))
			ret = -EFAULT;

	} else if (cmd == CMD_SET_REGULATOR){
		struct arg_set argset;
		if (copy_from_user(&argset, argp, sizeof(struct arg_set)))
			return -EFAULT;

		reg = devm_regulator_get(mdev->this_device, argset.info.name);
		if(IS_ERR(reg))
			return PTR_ERR(reg);

		ret = regulator_set_voltage(reg, argset.min, argset.max);

		if(ret < 0){
			dev_err(mdev->this_device,
					"Can not set regulator %s voltage %d\n",
					argset.info.name,
					ret);
			goto error;
		}

		ret = regulator_get_voltage(reg);
		if (ret < 0)
			goto error;

		argset.info.value = ret;

		if (copy_to_user(argp, &argset, sizeof(struct arg_info)))
			ret = -EFAULT;
	}

error:
	devm_regulator_put(reg);
	return ret;
}

static const struct file_operations mmm_fops = {
	.owner = THIS_MODULE,
	.unlocked_ioctl	= mmm_ioctl,
};

struct miscdevice mmm_dev = {
    .name = "mmm",
    .fops = &mmm_fops,
};

static int __init mmm_init(void){
	int ret = misc_register(&mmm_dev);
    if (ret) {
    	printk("Can not register %s driver: %d\n", mmm_dev.name, ret);
        return ret;
    }
	return 0;
};

static void __exit mmm_exit(void){
    misc_deregister(&mmm_dev);
};

module_init(mmm_init);
module_exit(mmm_exit);
MODULE_LICENSE("GPL");
