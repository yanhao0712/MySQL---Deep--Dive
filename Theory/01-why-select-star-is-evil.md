# 为什么select* 是初学者的陷阱


实验环境已就绪：已通过 Python 脚本（见 scripts/seed-data.py）向本地 MySQL 灌入 10 万条测试数据。后续将基于此大数据量进行 SELECT * 与指定列查询的性能对比实验。

例如
<img width="1155" height="1272" alt="image" src="https://github.com/user-attachments/assets/d26253ea-81a2-4d3e-b379-fb9bee0507b3" />



现在我们分别执行两条sql语句，用explain来对比他们之间的差异

以下是select *的结果
<img width="1170" height="152" alt="image" src="https://github.com/user-attachments/assets/85f05245-a707-483f-8494-1c9888270c73" />

<img width="1168" height="252" alt="image" src="https://github.com/user-attachments/assets/8a6e6d9a-6a64-40d0-a77a-1628dd02d1b7" />



如果我们不是查找*，而是查找其他的键呢

以下是查找主键（id）的结果

<img width="1182" height="195" alt="image" src="https://github.com/user-attachments/assets/667a0d6b-beb0-408b-b272-a38334c4386d" />

<img width="1171" height="214" alt="image" src="https://github.com/user-attachments/assets/459929c0-b725-4b12-92ac-aba90c498b4c" />




以下是查找其他键的结果
<img width="1186" height="188" alt="image" src="https://github.com/user-attachments/assets/e4b4d9a4-bdd4-4181-87b8-76a92927e113" />
<img width="1166" height="192" alt="image" src="https://github.com/user-attachments/assets/404ca92f-3d46-487f-bb5a-5ce079e8b81f" />





我们对比这几张图片，发现有以下不同
1. type
2. key 以及key_len
3. extra


首先 type是指这个select的依据，如果是*的话，由于它没有索引，所以会进行全表扫描，也就显示null，如果是我们的主键，它就会根据我们的索引（也就是key即图中的idx_email)进行查询 （这里的idx_email是覆盖索引，不是聚簇索引，要注意）
其次 key是指索引的名称，key_len是指通过key查找的字段，字段越多，查找的效率越高
最后 extra，这个是我们判断的最有力的证据，分为四个阶段
【第一阶段】Using index ，是指用了覆盖索引进行查询，不会产生回表 （这是因为b+树的特性，数据就在主键的下面，不需要回到磁盘）
【第二阶段】Using where ，是指索引过滤，可能回表
【第三阶段】Using filesort ，是指外部排序，开销大
【第四阶段】Using temporary，是指临时表，开销最大，是性能杀手




对比下来，我们不难发现用主键比用*查找快不止一个档次

你可能会问，那其他键呢？
我们在平时的sql编写时，会为了一些键编写索引，甚至是联合索引。因为我这里没有添加索引，所以它和*的效果都差不多。




所以在查找sql语句时，我们应该不用或者少用*，而是用那些有索引的键，这样能大大提升我们的性能。


最后你可能会问：我在mysql里面查询select * 和select （有索引的键）时，发现他们的用时基本差不多，有时甚至用*还更快。



第一：数据的吞吐不同。对于现在的磁盘和内存来说，那些小数据的io对磁盘的影响不大，所以看不出来差距（可能被网络io，建立联系等原因影响），但是如果数据量一大，比如上千万甚至是亿级别，我们就不得不进行调整。

第二： buffer pool 的缓存。 buffer pool 为了减少磁盘的io，会对你的查询做一个分辨，如果一个数据经常被用，（我们也称为 热数据）它就会把数据放在内存，而不会去磁盘寻找。


所以，分析一个sql语句应不应该优化，应该看explain ，而不是看时间。

















