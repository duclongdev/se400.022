import streamlit as st
from common.checkpassword import check_password
def main():
    """Hàm chính để chạy ứng dụng Streamlit."""
    st.set_page_config(layout="wide")
    st.title("Chào mừng bạn đến với Ứng dụng phân tích log của chúng tôi!")

    # Hiển thị biểu mẫu đăng nhập nếu chưa được xác thực
    if not check_password():
        st.stop()

    # Hiển thị nội dung của ứng dụng nếu đã xác thực
    st.write("Chào mừng bạn đến với ứng dụng của chúng tôi được xây dựng trên nền tảng Streamlit! 🎉")

    st.header("Thông tin về Ứng dụng")
    st.write("Ứng dụng của chúng tôi được thiết kế để phân tích các log không bình thường và cung cấp thông tin hữu ích để giải quyết vấn đề. Dù bạn là quản trị viên hệ thống, nhà phân tích dữ liệu hoặc nhà phát triển, ứng dụng của chúng tôi đều giúp bạn nắm bắt và giải quyết các vấn đề một cách nhanh chóng và hiệu quả.")

    st.header("Cách Sử Dụng")
    st.write("Sử dụng ứng dụng của chúng tôi đơn giản và trực quan:")
    st.write("1. **Đăng nhập**: Để bắt đầu, chỉ cần đăng nhập bằng tên người dùng và mật khẩu của bạn.")
    st.write("2. **Khám phá**: Khi đã đăng nhập, bạn sẽ có quyền truy cập vào các chức năng phân tích log, bao gồm tải lên tệp log, xử lý log và hiển thị kết quả.")
    st.write("3. **Tương tác**: Hãy thoải mái tương tác với các tính năng của ứng dụng để tìm kiếm thông tin và giải quyết vấn đề.")
    st.write("4. **Thưởng thức**: Chúng tôi hy vọng bạn sẽ thấy ứng dụng của chúng tôi hữu ích và hiệu quả trong công việc hàng ngày của bạn!")

    st.header("Thông Tin Quan Trọng")
    st.write("- Ứng dụng cần kết nối internet để hoạt động.")
    st.write("- Đảm bảo tệp log được định dạng đúng và không bị hỏng.")

    st.header("Phản Hồi")
    st.write("Chúng tôi luôn cố gắng cải thiện ứng dụng của chúng tôi! Nếu bạn có bất kỳ phản hồi, đề xuất hoặc gặp bất kỳ vấn đề nào, vui lòng liên hệ với chúng tôi. Ý kiến của bạn là quan trọng để giúp chúng tôi làm cho ứng dụng trở nên tốt hơn!")

if __name__ == '__main__':
    main()


