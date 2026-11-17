import type {
  ChatMessage,
  Conversation,
  Customer,
  DemoDatabase,
  Order,
  Ticket,
} from '@/types'
import { DEMO_AGENT_NAME } from '@/config'
import { truncate } from '@/utils/format'
import { buildWelcomeMessage } from './ai'

export const DB_VERSION = 1

function daysAgo(days: number, hour = 10, minute = 0): string {
  const date = new Date()
  date.setDate(date.getDate() - days)
  date.setHours(hour, minute, 0, 0)
  return date.toISOString()
}

function minutesAgo(minutes: number): string {
  return new Date(Date.now() - minutes * 60_000).toISOString()
}

export function createInitialDatabase(): DemoDatabase {
  const customers: Customer[] = [
    {
      id: 1,
      name: '林晓',
      phone: '13812345678',
      joinedAt: daysAgo(183, 14, 20),
    },
    {
      id: 2,
      name: '王磊',
      phone: '13987654321',
      joinedAt: daysAgo(96, 9, 12),
    },
    {
      id: 3,
      name: '陈雨',
      phone: '13755558888',
      joinedAt: daysAgo(42, 16, 8),
    },
  ]

  const conversations: Conversation[] = [
    {
      id: 101,
      customerId: 1,
      title: '耳机降噪异常咨询',
      status: 'closed',
      agentName: null,
      lastMessage: '',
      createdAt: daysAgo(3, 10, 1),
      updatedAt: daysAgo(2, 9, 30),
      waitingSince: null,
      closedAt: daysAgo(2, 9, 30),
    },
    {
      id: 104,
      customerId: 1,
      title: '保温杯换新咨询',
      status: 'closed',
      agentName: null,
      lastMessage: '',
      createdAt: daysAgo(8, 15, 6),
      updatedAt: daysAgo(7, 11, 20),
      waitingSince: null,
      closedAt: daysAgo(7, 11, 20),
    },
    {
      id: 105,
      customerId: 1,
      title: '想咨询退货流程',
      status: 'ai',
      agentName: null,
      lastMessage: '',
      createdAt: minutesAgo(22),
      updatedAt: minutesAgo(4),
      waitingSince: null,
      closedAt: null,
    },
    {
      id: 102,
      customerId: 2,
      title: '键盘一直未发货',
      status: 'waiting',
      agentName: null,
      lastMessage: '',
      createdAt: minutesAgo(50),
      updatedAt: minutesAgo(8),
      waitingSince: minutesAgo(30),
      closedAt: null,
    },
    {
      id: 103,
      customerId: 3,
      title: '卫衣尺码换货',
      status: 'human',
      agentName: DEMO_AGENT_NAME,
      lastMessage: '',
      createdAt: minutesAgo(70),
      updatedAt: minutesAgo(12),
      waitingSince: null,
      closedAt: null,
    },
  ]

  const messages: ChatMessage[] = [
    {
      id: 1,
      conversationId: 101,
      senderType: 'ai',
      content: buildWelcomeMessage('林晓'),
      createdAt: daysAgo(3, 10, 1),
    },
    {
      id: 2,
      conversationId: 101,
      senderType: 'customer',
      content: '你好，我买的无线降噪耳机右耳有轻微杂音，重新连接后还是有。',
      createdAt: daysAgo(3, 10, 4),
    },
    {
      id: 3,
      conversationId: 101,
      senderType: 'ai',
      content:
        '抱歉给您带来不好的体验。您可以先尝试重置耳机并重新配对；如果问题仍然存在，建议保留购买凭证和问题录音，我可以帮您记录售后需求。',
      createdAt: daysAgo(3, 10, 5),
    },
    {
      id: 4,
      conversationId: 101,
      senderType: 'customer',
      content: '试过了还是不行，那我先申请维修吧。',
      createdAt: daysAgo(3, 10, 8),
    },
    {
      id: 5,
      conversationId: 101,
      senderType: 'system',
      content: '会话已结束。',
      createdAt: daysAgo(2, 9, 30),
    },
    {
      id: 6,
      conversationId: 104,
      senderType: 'ai',
      content: buildWelcomeMessage('林晓'),
      createdAt: daysAgo(8, 15, 6),
    },
    {
      id: 7,
      conversationId: 104,
      senderType: 'customer',
      content: '保温杯的杯盖漏水，还在保修期内，可以换新吗？',
      createdAt: daysAgo(8, 15, 9),
    },
    {
      id: 8,
      conversationId: 104,
      senderType: 'ai',
      content:
        '杯盖漏水通常需要先确认是否为密封圈老化或使用方式问题。建议您拍摄杯盖和密封圈的细节照片，由人工客服进一步判断是否符合换新条件。',
      createdAt: daysAgo(8, 15, 10),
    },
    {
      id: 9,
      conversationId: 104,
      senderType: 'system',
      content: '会话已结束。',
      createdAt: daysAgo(7, 11, 20),
    },
    {
      id: 10,
      conversationId: 105,
      senderType: 'ai',
      content: buildWelcomeMessage('林晓'),
      createdAt: minutesAgo(22),
    },
    {
      id: 11,
      conversationId: 105,
      senderType: 'customer',
      content: '想咨询一下，如果耳机戴着不舒服可以退吗？',
      createdAt: minutesAgo(4),
    },
    {
      id: 12,
      conversationId: 102,
      senderType: 'ai',
      content: buildWelcomeMessage('王磊'),
      createdAt: minutesAgo(50),
    },
    {
      id: 13,
      conversationId: 102,
      senderType: 'customer',
      content: '我的机械键盘下单三天了还没发货，能帮我看看吗？',
      createdAt: minutesAgo(35),
    },
    {
      id: 14,
      conversationId: 102,
      senderType: 'ai',
      content:
        '我目前无法直接查询订单库，无法确认具体发货节点。如果订单已经超过承诺发货时间，建议您转人工让客服核实。',
      createdAt: minutesAgo(34),
    },
    {
      id: 15,
      conversationId: 102,
      senderType: 'customer',
      content: '转人工',
      createdAt: minutesAgo(31),
    },
    {
      id: 16,
      conversationId: 102,
      senderType: 'system',
      content: '已为您转接人工客服，请稍候。',
      createdAt: minutesAgo(30),
    },
    {
      id: 17,
      conversationId: 102,
      senderType: 'customer',
      content: '好的，麻烦尽快帮我看看，着急用。',
      createdAt: minutesAgo(8),
    },
    {
      id: 18,
      conversationId: 103,
      senderType: 'ai',
      content: buildWelcomeMessage('陈雨'),
      createdAt: minutesAgo(70),
    },
    {
      id: 19,
      conversationId: 103,
      senderType: 'customer',
      content: '刚收到的卫衣 L 码有点小，想换 XL，还有货吗？',
      createdAt: minutesAgo(55),
    },
    {
      id: 20,
      conversationId: 103,
      senderType: 'system',
      content: '已为您转接人工客服，请稍候。',
      createdAt: minutesAgo(54),
    },
    {
      id: 21,
      conversationId: 103,
      senderType: 'system',
      content: '客服小橙已接入会话。',
      createdAt: minutesAgo(50),
    },
    {
      id: 22,
      conversationId: 103,
      senderType: 'agent',
      content:
        '您好，我是客服小橙。XL 目前有库存，您这件商品也符合 7 天无理由换货条件。我先帮您登记换货工单，稍后会把寄回地址发给您。',
      createdAt: minutesAgo(47),
    },
    {
      id: 23,
      conversationId: 103,
      senderType: 'customer',
      content: '好的，谢谢，吊牌和包装都还在。',
      createdAt: minutesAgo(20),
    },
    {
      id: 24,
      conversationId: 103,
      senderType: 'agent',
      content: '收到，已为您创建换货工单，请保持手机畅通。',
      createdAt: minutesAgo(12),
    },
  ]

  const orders: Order[] = [
    {
      id: 1,
      orderNo: '202611010001',
      customerId: 1,
      productName: '无线降噪耳机 Pro',
      productSpec: '曜石黑 / 旗舰版',
      quantity: 1,
      amount: 899,
      orderStatus: 'shipped',
      logisticsCompany: '顺丰速运',
      trackingNo: 'SF1429384756102',
      createdAt: daysAgo(12, 20, 16),
      updatedAt: daysAgo(9, 8, 35),
    },
    {
      id: 2,
      orderNo: '202610280002',
      customerId: 1,
      productName: '轻量羽绒服',
      productSpec: '米白 / M',
      quantity: 1,
      amount: 599,
      orderStatus: 'received',
      logisticsCompany: '中通快递',
      trackingNo: 'ZT7384920165',
      createdAt: daysAgo(16, 11, 42),
      updatedAt: daysAgo(13, 16, 8),
    },
    {
      id: 3,
      orderNo: '202610200003',
      customerId: 1,
      productName: '智能保温杯',
      productSpec: '雾蓝 / 500ml',
      quantity: 1,
      amount: 129,
      orderStatus: 'completed',
      logisticsCompany: '圆通速递',
      trackingNo: 'YT9238471023',
      createdAt: daysAgo(24, 9, 20),
      updatedAt: daysAgo(20, 18, 30),
    },
    {
      id: 4,
      orderNo: '202611080004',
      customerId: 2,
      productName: '客制化机械键盘',
      productSpec: '茶轴 / 87 键',
      quantity: 1,
      amount: 469,
      orderStatus: 'pending_shipment',
      logisticsCompany: '待匹配',
      trackingNo: '—',
      createdAt: daysAgo(5, 21, 3),
      updatedAt: daysAgo(5, 21, 3),
    },
    {
      id: 5,
      orderNo: '202611050005',
      customerId: 2,
      productName: '轻量跑步鞋',
      productSpec: '黑 / 42',
      quantity: 1,
      amount: 329,
      orderStatus: 'refunding',
      logisticsCompany: '顺丰速运',
      trackingNo: 'SF1265839472101',
      createdAt: daysAgo(8, 13, 15),
      updatedAt: daysAgo(2, 10, 22),
    },
    {
      id: 6,
      orderNo: '202611100006',
      customerId: 3,
      productName: '宽松连帽卫衣',
      productSpec: '黑色 / L',
      quantity: 1,
      amount: 269,
      orderStatus: 'shipped',
      logisticsCompany: '京东物流',
      trackingNo: 'JDVA00928374615',
      createdAt: daysAgo(3, 22, 11),
      updatedAt: daysAgo(1, 8, 48),
    },
  ]

  const tickets: Ticket[] = [
    {
      id: 1,
      ticketNo: 'AS202611100001',
      orderId: 1,
      customerId: 1,
      conversationId: 101,
      type: 'repair',
      description: '无线降噪耳机右耳存在持续杂音，重新配对后问题依旧，申请检测维修。',
      priority: 'high',
      status: 'processing',
      assignee: DEMO_AGENT_NAME,
      createdAt: daysAgo(2, 9, 12),
      updatedAt: daysAgo(1, 15, 30),
      resolvedAt: null,
    },
    {
      id: 2,
      ticketNo: 'AS202611130002',
      orderId: 4,
      customerId: 2,
      conversationId: 102,
      type: 'logistics',
      description: '订单超过承诺发货时间仍未发货，客户着急使用，需要核实仓库发货进度。',
      priority: 'high',
      status: 'pending',
      assignee: DEMO_AGENT_NAME,
      createdAt: minutesAgo(24),
      updatedAt: minutesAgo(24),
      resolvedAt: null,
    },
    {
      id: 3,
      ticketNo: 'AS202611130003',
      orderId: 6,
      customerId: 3,
      conversationId: 103,
      type: 'exchange',
      description: '连帽卫衣 L 码偏小，客户申请更换 XL 码，商品吊牌包装完整。',
      priority: 'normal',
      status: 'processing',
      assignee: DEMO_AGENT_NAME,
      createdAt: minutesAgo(44),
      updatedAt: minutesAgo(12),
      resolvedAt: null,
    },
    {
      id: 4,
      ticketNo: 'AS202611090004',
      orderId: 3,
      customerId: 1,
      conversationId: null,
      type: 'repair',
      description: '智能保温杯杯盖密封圈老化导致漏水，已补发替换杯盖。',
      priority: 'low',
      status: 'resolved',
      assignee: DEMO_AGENT_NAME,
      createdAt: daysAgo(4, 14, 20),
      updatedAt: daysAgo(2, 10, 10),
      resolvedAt: daysAgo(2, 10, 10),
    },
  ]

  for (const conversation of conversations) {
    const latest = messages
      .filter((message) => message.conversationId === conversation.id)
      .sort((a, b) => a.id - b.id)
      .at(-1)
    if (latest) {
      conversation.lastMessage = truncate(latest.content, 80)
      conversation.updatedAt = latest.createdAt
    }
  }

  return {
    version: DB_VERSION,
    customers,
    conversations,
    messages,
    orders,
    tickets,
  }
}
