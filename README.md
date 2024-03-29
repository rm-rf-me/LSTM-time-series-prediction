# LSTM预测油田含水量

## 引言：

* 循环神经网络(Recurrent Neural Network， RNN)，是一种用于处理序列数据的神经网络。相比于一般的神经网络而言，该模型的每一次输出会综合考量当前输入和模型当前状态，并且在输出的同时模型也会对自身状态进行调节。从而该模型具备了非常好的序列数据处理能力。
* 但是RNN网络对数据的处理能力单一，对模型的维护能力较弱，训练过程中会存在梯度消失和梯度爆炸等问题。为了解决这些问题演化出了长短期记忆（Long-Short Term Memory， LSTM)模型，该模型能够很好的控制模型状态，对长期数据和短期数据都有很好的记忆能力。所以模型选择使用LSTM搭建。

## 背景：

* LSTM原理简述：

  * LSTM模型在时间序列上展开如图所示。每一个绿色方框都为t时刻的该模型本身。在t时刻时，模型接受三个输入值，分别为训练或预测数据的Xt，t-1时刻的输出状态Ht-1，t-1时刻的细胞状态Ct-1。经过模型内部的数据处理之后输出的同样为三个值：当前时刻的输出ht，和两个传递给下一时刻模型的Ht和Ct。
  * 而在模型内部通过激活函数构造了三个门结构，分别为：忘记门、输入门和输出门。
    * 其中忘记门及为图中最左边的分支，通过sigmoid激活函数处理上阶段输出和当前输入，来决定忘记哪些数据。这个门可以减少当前记忆信息的冗余度，抛弃无用信息。
    * 输入门为图片中间的分支，通过sigmoid激活函数处理上阶段输出和当前输入来决定要记住那些数据，并将该数据通过tanh激活函数处理后合并到模型的细胞状态上去，经过tanh激活函数主要是为了增强模型的非线性表达能力。
    * 输出门为图片中最右边的分支，通过sigmoid激活函数来决定当前要输出什么信息，同时将信息通过tanh激活函数处理后输出。

  

  ![6983308-169c41fa64ff202f](/home/zyn/乱七八遭/6983308-169c41fa64ff202f.png)

## 模型结构：

* 为了增强模型的拟合效果，实验采取了多层LSTM结构，并使用dropout层防止模型过拟合。详细的模型信息如图。一共包含三层lstm层，每一层的神经元个数都是100，并在第一和第三层之后加入dropout层。最后一层为100维到1维的全连接层获得总的输出，全连接层使用线性激活函数。
* 整个任务为时间序列上的回归任务，所以损失函数直接选择mse（mean_squared_error）。由于数据的周期性跨度较大，SGD的效果可能会比较不稳定，所以模型优化器选择adam。

![Screenshot from 2020-04-07 15-10-54](/home/zyn/乱七八遭/Screenshot from 2020-04-07 15-10-54.png)

## 数据处理：

* 首先将每一个观测数据的时间从时间格式转化到时间戳，从而具有时间数据的可预测性。同时为了模型的拟合效果对选择的数据进行归一化处理，将不同范围的数据映射到0附近的小区间内，能够增强模型的拟合能力。

* 经过对数据的分析可知，绝大部分油田数据都有3600个观测值。并且大多数的波动周期都在一分钟左右，也就是60个观测值左右。而有些数据在更广的数据范围上会呈现出更大的周期性变化，具体表现为在几百个到上千个不等的观测点之间会周期性的呈现疏密关系。所以一般的训练集和测试集比例可以为1：1，对于宏观周期范围变化不明显的数据集可以分割为3：7甚至1：9，都能够有比较稳定的预测结果。而对于具有比较明显宏观范围变化的数据则在分割的过程中训练集需要囊括至少一个宏观周期，通常可以为7：3或者9：1。

## 训练方法：

* 由于大部分数据的小范围周期都在一分钟以内，也就是在60个数据点以内，所以batchsize设置为64。并且经过大量的实验验证之后，对于一些周期比较明显、波动比较规律的数据在5个epoch左右loss会趋于稳定，也就是模型收敛。而对于一些周期不明显，波动幅度不定的数据通常需要10个epoch模型才能比较稳定。实验表明，对于绝大部分的油田数据5个epoch基本能够具有比较好的预测能力，对于变化的时间节点的把空都是比较准确的。本次实验的环境为Ubuntu18.04下6GB的GTX1060ti，对于64的batchsize下每个epoch的时间能够控制在10秒左右。

## 预测方法：

* 在对数据的预测过程中设置了两种预测模式：滑动窗口单点预测和滑动窗口整体预测
  * 滑动窗口单点预测：读取窗口长度个真实数据，预测下一时刻的数据。并且窗口向前移动一个时间点。为了覆盖大部分数据的至少一个周期，窗口长度通常为100。
  * 滑动窗口整体预测：读取历史数据中窗口长度个数据，预测下一时刻的数据，并且窗口向前移动一个时间点。与第一种方法的区别为历史数据中不全是真实数据，随着窗口的移动后半部分中的预测数据会越来越多，直到整个窗口全部为预测数据时，再开始使用全部真实数据进行新一轮的预测。

## 结果：

* 实验表明，该模型具有一下优点：
  * 小样本学习能力：训练数据只需要包含一个比较完整的周期数据，即可得到比较稳定的预测结果。正如数据处理时所描述的，对于宏观周期稳定的数据可以仅使用10%的数据作为训练集，这将大大提升模型的训练时间，从而具有实时预测的能力。
  * 模型拓展能力：在实验过程中出于效率和适应大部分数据的考虑模型采取了较为普适的结构和训练策略。在实际应用中可以根据具体的数据对模型结构和训练策略作更加细致的调整。并且经过实验验证，针对性的结构和策略能够进一步的提升模型拟合和预测的效果。
  * 在线模型更新：对于实时预测中一个很关键的点就是模型应该根据新的数据不断的进行修正。而本模型能够出色的完成这一点要求。能够在接受数据，预测下一时间点数据的同时，对模型自身状态进行修正。在实际应用中具有很强的鲁棒性。
