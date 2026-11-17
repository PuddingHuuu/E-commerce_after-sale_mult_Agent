export function buildWelcomeMessage(customerName: string): string {
  return `您好，${customerName}。我是橙心售后 AI 助理小橙，很高兴为您服务。\n\n您可以直接描述遇到的售后问题；如果需要人工客服跟进，请点击右上角的「转人工」。`
}

export function buildMockAiReply(question: string): string {
  const text = question.trim()

  if (/物流|快递|发货|到哪|签收|配送/.test(text)) {
    return [
      '我理解您想确认订单的物流进度。',
      '当前演示版本还没有接入实时订单与物流系统，无法直接查询包裹位置，请以订单详情中的物流信息为准。',
      '如果物流长时间没有更新，建议您点击「转人工」，客服可以进一步为您核实。',
    ].join('\n\n')
  }

  if (/退款|退钱|退货|退换/.test(text)) {
    return [
      '关于退款或退货，您可以先确认商品是否满足售后条件。一般情况下，商品签收后 7 天内支持无理由退货，定制类、已拆封的个护类商品等情况可能不适用。',
      '如果商品存在质量问题，建议您先保留商品照片和问题凭证；需要具体处理时，请点击「转人工」，客服会结合订单情况为您跟进。',
    ].join('\n\n')
  }

  if (/换货|尺码|颜色|型号/.test(text)) {
    return [
      '换货需要结合商品库存和订单当前状态判断。',
      '请先确认商品吊牌、包装完整，并保留购买凭证。您可以点击「转人工」，由人工客服协助核实换货条件并登记处理。',
    ].join('\n\n')
  }

  if (/质量|损坏|坏了|瑕疵|漏液|杂音|故障/.test(text)) {
    return [
      '非常抱歉给您带来困扰。',
      '建议您先拍摄能够清晰展示问题的照片或视频，并保留商品和包装。涉及质量问题的情况，人工客服可以进一步判断是维修、换货还是退款。',
      '需要立即处理的话，可以点击右上角「转人工」。',
    ].join('\n\n')
  }

  if (/人工|客服/.test(text)) {
    return '您可以点击页面右上角的「转人工」按钮，我会立即停止自动回复，并将当前对话转给人工客服。'
  }

  return [
    '收到您的问题，我正在为您整理售后处理建议。',
    '为了更快定位问题，您可以补充说明：商品名称、遇到的具体情况，以及期望的处理方式（退款、退货、换货或维修）。',
    '如果您希望由人工客服直接处理，可以点击右上角「转人工」。',
  ].join('\n\n')
}

export function simulateNetworkDelay(): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, 800 + Math.random() * 500)
  })
}
