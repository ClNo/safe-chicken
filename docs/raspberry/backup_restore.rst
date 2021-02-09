Backup and Restore
==================

Here you learn how to backup the flash card containing the operating system and your application in case it's getting
lost and you want to restore it later.

Plug in your Raspberry's flash card in a desktop PC, then start a partition manager like *gparted* or *kdepartitionmanager*.

.. note::

   In this example, the flash disk is on **/dev/sdb**, /dev/sdb2 is the main partition.

Prepare Flash Card
------------------

First fill the unused space with zeros before you want to compress it.

.. code-block::

   sudo mkdir -p /mnt/work
   sudo mount /dev/sdb2 /mnt/work
   sudo dd if=/dev/zero of=/mnt/work/zero bs=1M
   sudo rm /mnt/work/zero

Then shrink the partition to a minimum:

- First unmount the partition :code:`sudo umount /mnt/work`
- start the partition manager
- in my example: shrink sdb2 from 16/32GB flash card size to around 2 GB


Backup on Linux
---------------

Write the flash disk into a file; use gzip which compresses enough (using the compressor *pigz*).

.. code-block::

   sudo umount /mnt/work
   time sudo bash -c "dd if=/dev/sdb bs=1M | pigz -9 > safechicken_16gb_image_raspberry_$(date -I).dd.gz"
   # size: around 623 MiB
   sudo chown ${USER}:${USER} safechicken*


Restore on Linux
----------------

.. warning::

   This may overwrite your harddisk if you choose the wrong disk! Here, it is **/dev/sdb**.

.. code-block::

   time sudo bash -c "pigz -dc safechicken_16gb_image_raspberry_DATE.dd.gz | dd of=/dev/sdb bs=1M"
