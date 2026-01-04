"""
Script to analyze interaction logs and generate statistics.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def analyze_logs(log_file: str = "./logs/interactions.jsonl"):
    """
    Analyze interaction logs and print statistics.
    
    Args:
        log_file: Path to the interaction log file
    """
    log_path = Path(log_file)
    
    if not log_path.exists():
        logger.error(f"Log file not found: {log_file}")
        return
    
    # Statistics
    total_queries = 0
    total_response_time = 0.0
    questions_by_hour = defaultdict(int)
    questions_by_type = defaultdict(int)
    average_question_length = 0
    average_answer_length = 0
    
    # Read logs
    interactions = []
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    interaction = json.loads(line)
                    interactions.append(interaction)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON line: {e}")
    
    # Analyze
    for interaction in interactions:
        total_queries += 1
        total_response_time += interaction.get('response_time', 0)
        
        # Parse timestamp
        timestamp = datetime.fromisoformat(interaction['timestamp'])
        hour = timestamp.hour
        questions_by_hour[hour] += 1
        
        # Question length
        question = interaction.get('question', '')
        average_question_length += len(question)
        
        # Answer length
        answer = interaction.get('answer', '')
        average_answer_length += len(answer)
        
        # Categorize by keywords
        if any(kw in question for kw in ['退费', '退款', '退课']):
            questions_by_type['退费相关'] += 1
        elif any(kw in question for kw in ['价格', '多少钱', '费用']):
            questions_by_type['价格相关'] += 1
        elif any(kw in question for kw in ['课程', '内容', '学什么']):
            questions_by_type['课程内容'] += 1
        elif any(kw in question for kw in ['时间', '多久', '周期']):
            questions_by_type['时间相关'] += 1
        else:
            questions_by_type['其他'] += 1
    
    # Calculate averages
    if total_queries > 0:
        avg_response_time = total_response_time / total_queries
        average_question_length = average_question_length / total_queries
        average_answer_length = average_answer_length / total_queries
    else:
        avg_response_time = 0
    
    # Print report
    print("\n" + "=" * 60)
    print("📊 交互日志分析报告")
    print("=" * 60)
    
    print(f"\n📈 总体统计:")
    print(f"  总查询数: {total_queries}")
    print(f"  平均响应时间: {avg_response_time:.2f}秒")
    print(f"  平均问题长度: {average_question_length:.0f}字符")
    print(f"  平均答案长度: {average_answer_length:.0f}字符")
    
    print(f"\n🏷️  问题分类统计:")
    for category, count in sorted(questions_by_type.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_queries * 100) if total_queries > 0 else 0
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    print(f"\n⏰ 按小时统计:")
    sorted_hours = sorted(questions_by_hour.items())
    for hour, count in sorted_hours[:10]:  # Top 10 hours
        print(f"  {hour:02d}:00 - {count}次查询")
    
    print(f"\n🔝 最近10次查询:")
    for i, interaction in enumerate(interactions[-10:], 1):
        timestamp = interaction['timestamp'].split('T')[1][:8]
        question = interaction['question'][:40] + "..." if len(interaction['question']) > 40 else interaction['question']
        print(f"  {i}. [{timestamp}] {question}")
    
    print("\n" + "=" * 60)
    
    # Export to CSV
    csv_file = log_path.parent / "interactions_analysis.csv"
    try:
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("时间戳,会话ID,问题,答案长度,响应时间,来源数量\n")
            for interaction in interactions:
                timestamp = interaction['timestamp']
                session_id = interaction['session_id']
                question = interaction['question'].replace(',', '，')
                answer_len = len(interaction['answer'])
                response_time = interaction['response_time']
                sources_count = len(interaction.get('sources', []))
                
                f.write(f"{timestamp},{session_id},{question},{answer_len},{response_time:.2f},{sources_count}\n")
        
        print(f"✅ 分析结果已导出到: {csv_file}")
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import sys
    
    log_file = sys.argv[1] if len(sys.argv) > 1 else "./logs/interactions.jsonl"
    analyze_logs(log_file)
